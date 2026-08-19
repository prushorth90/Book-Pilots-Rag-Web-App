from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import joblib
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from app.models.book import Book

CONTENT_ARTIFACT = "content.joblib"


@dataclass(frozen=True)
class ContentArtifacts:
    book_ids: list[int]
    vectorizer: TfidfVectorizer
    matrix: csr_matrix


def book_document(book: Book) -> str:
    genres = " ".join(book.genres or [])
    return " ".join(
        [
            f"genre_{genres} {genres} {genres}",
            f"author_{book.author} {book.author}",
            f"title_{book.title} {book.title}",
            book.description or "",
        ]
    )


def prepare_content_features(books: Iterable[Book]) -> ContentArtifacts:
    catalog = list(books)
    if not catalog:
        raise ValueError("At least one saved book is required to train content features")
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=20_000,
        strip_accents="unicode",
    )
    matrix = vectorizer.fit_transform(book_document(book) for book in catalog).tocsr()
    return ContentArtifacts(
        book_ids=[book.id for book in catalog], vectorizer=vectorizer, matrix=matrix
    )


def save_content_artifacts(artifacts: ContentArtifacts, artifact_dir: Path) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    destination = artifact_dir / CONTENT_ARTIFACT
    joblib.dump(artifacts, destination)
    return destination


def load_content_artifacts(artifact_dir: Path) -> ContentArtifacts:
    artifact = joblib.load(artifact_dir / CONTENT_ARTIFACT)
    if not isinstance(artifact, ContentArtifacts):
        raise ValueError("Invalid content recommendation artifact")
    return artifact
