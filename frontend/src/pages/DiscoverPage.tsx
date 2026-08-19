import { Search } from "lucide-react";
import { useState, type FormEvent } from "react";

import { searchBooks } from "../api/books";
import { BookCard } from "../components/BookCard";
import type { Book, SearchField } from "../types/books";

export function DiscoverPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true); setError(null);
    try {
      const result = await searchBooks(String(form.get("query")), String(form.get("field")) as SearchField);
      setBooks(result.books); setTotal(result.total); setSearched(true);
    } catch {
      setError("Open Library could not be reached. Please try again.");
    } finally { setLoading(false); }
  }

  return (
    <section className="discover-page">
      <p className="kicker">Open Library catalogue</p>
      <h1>Discover your next book.</h1>
      <form className="search-bar" onSubmit={search}>
        <select name="field" aria-label="Search by">
          <option value="keyword">Keyword</option><option value="title">Title</option>
          <option value="author">Author</option><option value="isbn">ISBN</option>
        </select>
        <input name="query" aria-label="Book search" placeholder="Search millions of books" required />
        <button type="submit" aria-label="Search" disabled={loading}><Search size={20} /></button>
      </form>
      {error ? <p role="alert" className="form-error">{error}</p> : null}
      {searched ? <p className="result-count">Showing {books.length} of {total.toLocaleString()} results</p> : <p className="discover-prompt">Search by title, author, ISBN, or any keyword.</p>}
      <div className="book-grid">{books.map((book) => <BookCard key={book.open_library_key} book={book} />)}</div>
    </section>
  );
}