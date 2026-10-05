from __future__ import annotations

import argparse
import asyncio
import csv
import json
import shutil
from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import kagglehub
from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from app.database.session import SessionLocal
from app.models.book import Book, ExternalRating

SOURCE = "book-crossing"
DATASET = "arashnic/book-recommendation-dataset"


@dataclass(frozen=True)
class ExternalRatingRow:
    user_id: int
    isbn: str
    rating: int


def normalize_isbn(value: str) -> str:
    return "".join(character for character in value.upper().strip() if character.isalnum())


def normalize_rating(value: int) -> int:
    return max(1, min(5, (value + 1) // 2))


def dict_reader(source: TextIO) -> csv.DictReader[str]:
    header = source.readline()
    source.seek(0)
    delimiter = ";" if header.count(";") > header.count(",") else ","
    return csv.DictReader(source, delimiter=delimiter, quotechar='"')


def explicit_ratings(path: Path) -> Iterator[ExternalRatingRow]:
    with path.open(encoding="latin-1", newline="") as source:
        reader = dict_reader(source)
        for row in reader:
            try:
                raw_rating = int(row["Book-Rating"])
                user_id = int(row["User-ID"])
            except (KeyError, TypeError, ValueError):
                continue
            isbn = normalize_isbn(row.get("ISBN", ""))
            if raw_rating <= 0 or not isbn:
                continue
            yield ExternalRatingRow(user_id=user_id, isbn=isbn, rating=normalize_rating(raw_rating))


def selected_ratings(
    ratings_path: Path,
    min_user_ratings: int,
    min_book_ratings: int,
    max_books: int | None,
) -> tuple[list[ExternalRatingRow], set[str]]:
    user_counts = Counter(row.user_id for row in explicit_ratings(ratings_path))
    eligible_users = {
        user_id for user_id, count in user_counts.items() if count >= min_user_ratings
    }
    book_counts = Counter(
        row.isbn for row in explicit_ratings(ratings_path) if row.user_id in eligible_users
    )
    eligible_books = [
        isbn for isbn, count in book_counts.most_common() if count >= min_book_ratings
    ]
    if max_books is not None:
        eligible_books = eligible_books[:max_books]
    selected_books = set(eligible_books)
    ratings = [
        row
        for row in explicit_ratings(ratings_path)
        if row.user_id in eligible_users and row.isbn in selected_books
    ]
    return ratings, selected_books


def book_rows(path: Path, selected_books: set[str]) -> list[dict[str, object]]:
    rows_by_isbn: dict[str, dict[str, object]] = {}
    with path.open(encoding="latin-1", newline="") as source:
        reader = dict_reader(source)
        for row in reader:
            isbn = normalize_isbn(row.get("ISBN", ""))
            if isbn not in selected_books:
                continue
            try:
                raw_year = int(row.get("Year-Of-Publication", "0"))
            except ValueError:
                raw_year = 0
            year = raw_year if 1000 <= raw_year <= 2100 else None
            candidate: dict[str, object] = {
                "open_library_key": f"BX:{isbn}",
                "title": row.get("Book-Title", "").strip() or "Untitled",
                "author": row.get("Book-Author", "").strip() or "Unknown author",
                "description": None,
                "isbn": isbn,
                "cover_image_url": row.get("Image-URL-L", "").strip() or None,
                "publication_year": year,
                "genres": [],
                "average_rating": None,
            }
            existing = rows_by_isbn.get(isbn)
            if existing is None or (
                existing["cover_image_url"] is None and candidate["cover_image_url"] is not None
            ):
                rows_by_isbn[isbn] = candidate
    return list(rows_by_isbn.values())


def download_dataset(data_dir: Path) -> None:
    cache_dir = Path(kagglehub.dataset_download(DATASET))
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("Books.csv", "Ratings.csv", "Users.csv"):
        shutil.copy2(cache_dir / filename, data_dir / filename)


async def import_dataset(
    data_dir: Path,
    min_user_ratings: int,
    min_book_ratings: int,
    max_books: int | None,
) -> dict[str, int]:
    ratings, selected_books = selected_ratings(
        data_dir / "Ratings.csv", min_user_ratings, min_book_ratings, max_books
    )
    books = book_rows(data_dir / "Books.csv", selected_books)
    found_isbns = {str(book["isbn"]) for book in books}
    ratings = [rating for rating in ratings if rating.isbn in found_isbns]
    rating_values: dict[str, list[int]] = defaultdict(list)
    for rating in ratings:
        rating_values[rating.isbn].append(rating.rating)
    for book in books:
        values = rating_values[str(book["isbn"])]
        book["average_rating"] = round(sum(values) / len(values), 2) if values else None

    async with SessionLocal() as db:
        await db.execute(delete(ExternalRating).where(ExternalRating.source == SOURCE))
        dialect = db.bind.dialect.name if db.bind else ""
        for offset in range(0, len(books), 1000):
            batch = books[offset : offset + 1000]
            if dialect == "postgresql":
                statement = postgresql_insert(Book).values(batch)
                statement = statement.on_conflict_do_update(
                    index_elements=[Book.open_library_key],
                    set_={
                        "title": statement.excluded.title,
                        "author": statement.excluded.author,
                        "isbn": statement.excluded.isbn,
                        "cover_image_url": statement.excluded.cover_image_url,
                        "publication_year": statement.excluded.publication_year,
                        "average_rating": statement.excluded.average_rating,
                    },
                )
                await db.execute(statement)
            else:
                await db.execute(insert(Book), batch)
        await db.commit()

        isbn_rows = await db.execute(
            select(Book.id, Book.isbn).where(Book.open_library_key.like("BX:%"))
        )
        book_ids = {isbn: book_id for book_id, isbn in isbn_rows if isbn}
        external_rows = [
            {
                "source": SOURCE,
                "external_user_id": -rating.user_id,
                "book_id": book_ids[rating.isbn],
                "rating": rating.rating,
            }
            for rating in ratings
            if rating.isbn in book_ids
        ]
        for offset in range(0, len(external_rows), 5000):
            await db.execute(insert(ExternalRating), external_rows[offset : offset + 5000])
        await db.commit()

    return {
        "books": len(books),
        "ratings": len(external_rows),
        "users": len({rating.user_id for rating in ratings}),
    }


async def run(arguments: argparse.Namespace) -> None:
    data_dir = Path(arguments.data_dir)
    if arguments.download or not (data_dir / "Books.csv").exists():
        download_dataset(data_dir)
    result = await import_dataset(
        data_dir,
        arguments.min_user_ratings,
        arguments.min_book_ratings,
        arguments.max_books,
    )
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the CC0 Book-Crossing Kaggle dataset")
    parser.add_argument("--data-dir", default="data/book-crossing")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--min-user-ratings", type=int, default=20)
    parser.add_argument("--min-book-ratings", type=int, default=10)
    parser.add_argument("--max-books", type=int, default=25_000)
    arguments = parser.parse_args()
    asyncio.run(run(arguments))


if __name__ == "__main__":
    main()
