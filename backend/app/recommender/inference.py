from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book, UserBook, UserGenre
from app.recommender.feature_preparation import ContentArtifacts, load_content_artifacts
from app.recommender.model_training import COLLABORATIVE_METADATA, COLLABORATIVE_MODEL


class RecommendationEngine:
    def __init__(self, artifact_dir: Path, min_ratings: int = 3) -> None:
        self.artifact_dir = artifact_dir
        self.min_ratings = min_ratings
        self._content: ContentArtifacts | None = None
        self._collaborative_model: Any = None
        self._collaborative_metadata: dict[str, Any] = {}
        self._popularity: dict[str, float] = {}

    def _load_artifacts(self) -> ContentArtifacts:
        if self._content is None:
            self._content = load_content_artifacts(self.artifact_dir)
            manifest_path = self.artifact_dir / "manifest.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self._popularity = manifest.get("popularity", {})
            metadata_path = self.artifact_dir / COLLABORATIVE_METADATA
            model_path = self.artifact_dir / COLLABORATIVE_MODEL
            if metadata_path.exists() and model_path.exists():
                import tensorflow as tf

                self._collaborative_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                self._collaborative_model = tf.keras.models.load_model(model_path)
        return self._content

    async def recommend(
        self, db: AsyncSession, user_id: int, limit: int = 10
    ) -> list[tuple[Book, float, str]]:
        content = self._load_artifacts()
        books = list(
            (await db.execute(select(Book).where(Book.id.in_(content.book_ids)))).scalars().all()
        )
        book_by_id = {book.id: book for book in books}
        history = list(
            (await db.execute(select(UserBook).where(UserBook.user_id == user_id)))
            .unique()
            .scalars()
            .all()
        )
        preferences = list(
            (await db.execute(select(UserGenre.genre).where(UserGenre.user_id == user_id)))
            .scalars()
            .all()
        )
        rated = [entry for entry in history if entry.rating is not None]
        excluded = {entry.book_id for entry in history}
        profile_parts = preferences * 3
        for entry in rated:
            if entry.rating and entry.rating >= 4:
                profile_parts.extend([entry.book.title, entry.book.author, *entry.book.genres])
        profile = " ".join(profile_parts) or "books reading literature"
        profile_vector = content.vectorizer.transform([profile])
        content_scores = cosine_similarity(profile_vector, content.matrix).ravel()
        collaborative_scores = self._collaborative_scores(user_id, content.book_ids)
        use_collaborative = len(rated) >= self.min_ratings and collaborative_scores is not None

        recommendations: list[tuple[Book, float, str]] = []
        for index, book_id in enumerate(content.book_ids):
            book = book_by_id.get(book_id)
            if not book or book_id in excluded:
                continue
            content_score = float(content_scores[index])
            popularity = float(self._popularity.get(str(book_id), 0.0))
            if use_collaborative and collaborative_scores is not None:
                score = (
                    0.55 * collaborative_scores[index] + 0.35 * content_score + 0.10 * popularity
                )
                explanation = self._hybrid_explanation(book, preferences, content_score)
            else:
                score = 0.90 * content_score + 0.10 * popularity
                explanation = self._cold_start_explanation(book, preferences)
            recommendations.append((book, round(float(score), 4), explanation))
        return sorted(recommendations, key=lambda item: item[1], reverse=True)[:limit]

    def _collaborative_scores(
        self, user_id: int, book_ids: list[int]
    ) -> NDArray[np.float32] | None:
        if self._collaborative_model is None:
            return None
        user_map = self._collaborative_metadata.get("user_map", {})
        book_map = self._collaborative_metadata.get("book_map", {})
        user_index = user_map.get(str(user_id))
        if user_index is None:
            return None
        known_positions = [
            (position, book_map.get(str(book_id))) for position, book_id in enumerate(book_ids)
        ]
        valid = [(position, index) for position, index in known_positions if index is not None]
        scores = np.full(len(book_ids), 0.5, dtype=np.float32)
        if valid:
            predictions = self._collaborative_model.predict(
                {
                    "user": np.full(len(valid), user_index, dtype=np.int32),
                    "book": np.asarray([index for _, index in valid], dtype=np.int32),
                },
                verbose=0,
            ).reshape(-1)
            for (position, _), prediction in zip(valid, predictions, strict=True):
                scores[position] = prediction
        return scores

    @staticmethod
    def _cold_start_explanation(book: Book, preferences: list[str]) -> str:
        matches = sorted(
            {genre.lower() for genre in book.genres} & {genre.lower() for genre in preferences}
        )
        if matches:
            return f"Matches your interest in {', '.join(matches[:2])}."
        return "Matches the themes in your reading preferences."

    @staticmethod
    def _hybrid_explanation(book: Book, preferences: list[str], content_score: float) -> str:
        matches = sorted(
            {genre.lower() for genre in book.genres} & {genre.lower() for genre in preferences}
        )
        if matches:
            return f"Readers with similar ratings also enjoyed this {matches[0]} book."
        if content_score > 0.1:
            return "Similar to books you rated highly and liked by comparable readers."
        return "Recommended from your rating patterns and community interest."
