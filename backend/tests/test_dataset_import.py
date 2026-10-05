import csv
from pathlib import Path

from app.recommender.dataset_import import (
    book_rows,
    normalize_isbn,
    normalize_rating,
    selected_ratings,
)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="latin-1", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames, delimiter=";", quotechar='"')
        writer.writeheader()
        writer.writerows(rows)


def test_book_crossing_normalization_and_filtering(tmp_path: Path) -> None:
    ratings_path = tmp_path / "Ratings.csv"
    books_path = tmp_path / "Books.csv"
    write_csv(
        ratings_path,
        ["User-ID", "ISBN", "Book-Rating"],
        [
            {"User-ID": 1, "ISBN": "0-123", "Book-Rating": 10},
            {"User-ID": 1, "ISBN": "0-456", "Book-Rating": 8},
            {"User-ID": 2, "ISBN": "0-123", "Book-Rating": 0},
        ],
    )
    write_csv(
        books_path,
        [
            "ISBN",
            "Book-Title",
            "Book-Author",
            "Year-Of-Publication",
            "Image-URL-L",
        ],
        [
            {
                "ISBN": "0-123",
                "Book-Title": "A Real Book",
                "Book-Author": "An Author",
                "Year-Of-Publication": 2001,
                "Image-URL-L": "https://example.com/cover.jpg",
            },
            {
                "ISBN": "0-456",
                "Book-Title": "Another Book",
                "Book-Author": "Another Author",
                "Year-Of-Publication": 2002,
                "Image-URL-L": "",
            },
            {
                "ISBN": "0456",
                "Book-Title": "Duplicate Edition",
                "Book-Author": "Another Author",
                "Year-Of-Publication": 2002,
                "Image-URL-L": "https://example.com/better-cover.jpg",
            },
        ],
    )

    ratings, selected = selected_ratings(ratings_path, 2, 1, None)
    books = book_rows(books_path, selected)

    assert normalize_isbn("0-123") == "0123"
    assert normalize_rating(10) == 5
    assert normalize_rating(1) == 1
    assert len(ratings) == 2
    assert len(books) == 2
    assert {book["open_library_key"] for book in books} == {"BX:0123", "BX:0456"}
