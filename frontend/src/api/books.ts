import { apiClient } from "./client";
import type { Book, BookSearchResponse, LibraryEntry, ReadingStatus, SearchField } from "../types/books";

export function searchBooks(query: string, field: SearchField): Promise<BookSearchResponse> {
  const params = new URLSearchParams({ query, field });
  return apiClient.get<BookSearchResponse>(`/books/search?${params}`);
}

export function getBookDetails(workId: string): Promise<Book> {
  return apiClient.get<Book>(`/books/details/${encodeURIComponent(workId)}`);
}

export function getLibrary(): Promise<LibraryEntry[]> {
  return apiClient.get<LibraryEntry[]>("/books/library");
}

export function saveToLibrary(
  book: Book,
  status: ReadingStatus,
  rating: number | null,
  review: string | null,
): Promise<LibraryEntry> {
  return apiClient.put<LibraryEntry>("/books/library", { book, status, rating, review });
}

export function removeFromLibrary(workId: string): Promise<void> {
  return apiClient.delete(`/books/library/${encodeURIComponent(workId)}`);
}

export function getPreferences(): Promise<{ genres: string[] }> {
  return apiClient.get<{ genres: string[] }>("/books/preferences");
}

export function savePreferences(genres: string[]): Promise<{ genres: string[] }> {
  return apiClient.put<{ genres: string[] }>("/books/preferences", { genres });
}