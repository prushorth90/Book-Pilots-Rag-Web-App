from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import select

from app.config import get_settings
from app.database.session import SessionLocal
from app.models.book import Book, ExternalRating, UserBook
from app.recommender.feature_preparation import prepare_content_features, save_content_artifacts
from app.recommender.model_training import train_collaborative_model


async def train(epochs: int) -> None:
    settings = get_settings()
    async with SessionLocal() as db:
        books = list((await db.execute(select(Book).order_by(Book.id))).scalars().all())
        ratings = list(
            (
                await db.execute(
                    select(UserBook.user_id, UserBook.book_id, UserBook.rating).where(
                        UserBook.rating.is_not(None)
                    )
                )
            ).all()
        )
        external_ratings = list(
            (
                await db.execute(
                    select(
                        ExternalRating.external_user_id,
                        ExternalRating.book_id,
                        ExternalRating.rating,
                    )
                )
            ).all()
        )
    content = prepare_content_features(books)
    save_content_artifacts(content, settings.recommender_artifact_dir)
    app_rating_values = [(int(row[0]), int(row[1]), int(row[2])) for row in ratings]
    external_rating_values = [(int(row[0]), int(row[1]), int(row[2])) for row in external_ratings]
    typed_ratings = [*app_rating_values, *external_rating_values]
    collaborative_trained = train_collaborative_model(
        typed_ratings, settings.recommender_artifact_dir, epochs
    )
    counts: dict[int, list[int]] = defaultdict(list)
    for _, book_id, rating in typed_ratings:
        counts[book_id].append(rating)
    popularity = {
        str(book_id): round((sum(values) / len(values)) / 5, 4)
        for book_id, values in counts.items()
    }
    manifest = {
        "trained_at": datetime.now(UTC).isoformat(),
        "book_count": len(books),
        "rating_count": len(typed_ratings),
        "external_rating_count": len(external_ratings),
        "collaborative_trained": collaborative_trained,
        "popularity": popularity,
    }
    (settings.recommender_artifact_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Book Pilots recommendation artifacts")
    parser.add_argument("--epochs", type=int, default=20)
    arguments = parser.parse_args()
    asyncio.run(train(arguments.epochs))


if __name__ == "__main__":
    main()
