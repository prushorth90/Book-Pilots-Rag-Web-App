import { useState } from "react";

import { saveToLibrary } from "../api/books";
import type { Book, ReadingStatus } from "../types/books";
import { RatingControl } from "./RatingControl";

interface Props {
  book: Book;
  initialStatus?: ReadingStatus;
  initialRating?: number | null;
  initialReview?: string | null;
  compact?: boolean;
}

export function ReadingListControls({ book, initialStatus = "WANT_TO_READ", initialRating = null, initialReview = "", compact = false }: Props) {
  const [status, setStatus] = useState<ReadingStatus>(initialStatus);
  const [rating, setRating] = useState<number | null>(initialRating);
  const [review, setReview] = useState(initialReview ?? "");
  const [message, setMessage] = useState<string | null>(null);

  async function save() {
    setMessage("Saving...");
    try {
      await saveToLibrary(book, status, rating, review || null);
      setMessage("Saved to your library");
    } catch {
      setMessage("Could not save this book");
    }
  }

  return (
    <div className={`reading-controls ${compact ? "compact" : ""}`}>
      <label>
        Reading status
        <select value={status} onChange={(event) => setStatus(event.target.value as ReadingStatus)}>
          <option value="WANT_TO_READ">Want to read</option>
          <option value="READING">Reading</option>
          <option value="READ">Read</option>
        </select>
      </label>
      {!compact ? <><RatingControl value={rating} onChange={setRating} /><label>Review<textarea value={review} maxLength={5000} onChange={(event) => setReview(event.target.value)} placeholder="What stayed with you?" /></label></> : null}
      <button className="save-book" type="button" onClick={save}>Save</button>
      <span className="save-message" aria-live="polite">{message}</span>
    </div>
  );
}