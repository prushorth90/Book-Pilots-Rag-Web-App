import { useEffect, useState } from "react";

import { getLibrary, removeFromLibrary } from "../api/books";
import { BookCard } from "../components/BookCard";
import type { LibraryEntry } from "../types/books";

export function LibraryPage() {
  const [entries, setEntries] = useState<LibraryEntry[]>([]);
  useEffect(() => { getLibrary().then(setEntries).catch(() => setEntries([])); }, []);
  async function remove(workId: string) {
    await removeFromLibrary(workId);
    setEntries((current) => current.filter((entry) => entry.book.open_library_key !== workId));
  }
  return (
    <section className="library-page">
      <p className="kicker">Reading history</p><h1>Your library.</h1>
      {!entries.length ? <p>Your saved books will appear here.</p> : null}
      <div className="book-grid">{entries.map((entry) => <div className="library-item" key={entry.id}><BookCard book={entry.book} entry={entry} /><p>{entry.status.replaceAll("_", " ")}{entry.rating ? ` · ${entry.rating}/5` : ""}</p>{entry.review ? <blockquote>{entry.review}</blockquote> : null}<button type="button" onClick={() => remove(entry.book.open_library_key)}>Remove</button></div>)}</div>
    </section>
  );
}