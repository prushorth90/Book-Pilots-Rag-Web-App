import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import { getBookDetails } from "../api/books";
import { BookCover } from "../components/BookCover";
import { ReadingListControls } from "../components/ReadingListControls";
import type { Book } from "../types/books";

export function BookDetailsPage() {
  const { workId = "" } = useParams();
  const location = useLocation();
  const initial = (location.state as { book?: Book } | null)?.book ?? null;
  const [book, setBook] = useState<Book | null>(initial);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (initial) return;
    getBookDetails(workId).then(setBook).catch(() => setError(true));
  }, [initial, workId]);

  if (error) return <p className="route-loading">This book could not be loaded.</p>;
  if (!book) return <p className="route-loading">Loading book...</p>;
  return (
    <section className="book-details-page">
      <BookCover url={book.cover_image_url} title={book.title} />
      <div className="book-details-copy">
        <p className="kicker">{book.publication_year ?? "Publication year unknown"}</p>
        <h1>{book.title}</h1><p className="book-author">by {book.author}</p>
        <p className="book-description">{book.description ?? "No description is available for this edition."}</p>
        <div className="book-meta"><span>ISBN {book.isbn ?? "unavailable"}</span><span>Open Library {book.open_library_key}</span>{book.average_rating ? <span>Community rating {book.average_rating}/5</span> : null}</div>
        {book.genres.length ? <div className="genre-list">{book.genres.map((genre) => <span key={genre}>{genre}</span>)}</div> : null}
        <ReadingListControls book={book} />
      </div>
    </section>
  );
}