import { Link } from "react-router-dom";

import type { Book, LibraryEntry } from "../types/books";
import { BookCover } from "./BookCover";
import { ReadingListControls } from "./ReadingListControls";

export function BookCard({ book, entry }: { book: Book; entry?: LibraryEntry }) {
  return (
    <article className="book-card">
      <Link to={`/books/${book.open_library_key}`} state={{ book }}><BookCover url={book.cover_image_url} title={book.title} /></Link>
      <div className="book-card-copy">
        <p>{book.publication_year ?? "Year unknown"}</p>
        <h2><Link to={`/books/${book.open_library_key}`} state={{ book }}>{book.title}</Link></h2>
        <span>{book.author}</span>
      </div>
      <ReadingListControls
        book={book}
        compact
        initialStatus={entry?.status}
        initialRating={entry?.rating}
        initialReview={entry?.review}
      />
    </article>
  );
}