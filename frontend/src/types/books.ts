export type SearchField = "keyword" | "title" | "author" | "isbn";
export type ReadingStatus = "WANT_TO_READ" | "READING" | "READ";

export interface Book {
  id?: number | null;
  open_library_key: string;
  title: string;
  author: string;
  description: string | null;
  isbn: string | null;
  cover_image_url: string | null;
  publication_year: number | null;
  genres: string[];
  average_rating: number | null;
}

export interface BookSearchResponse {
  total: number;
  books: Book[];
}

export interface LibraryEntry {
  id: number;
  status: ReadingStatus;
  rating: number | null;
  review: string | null;
  book: Book;
}