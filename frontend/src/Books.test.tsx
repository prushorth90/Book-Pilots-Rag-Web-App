import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = { id: 1, username: "reader", email: "r@example.com", first_name: "Ada", last_name: "Reader", created_at: "2026-01-01T00:00:00Z" };
const book = { open_library_key: "OL1W", title: "The Test Book", author: "A. Writer", description: null, isbn: null, cover_image_url: null, publication_year: null, genres: [], average_rating: null };

beforeEach(() => { localStorage.setItem("book-pilots-access-token", "token"); window.history.replaceState({}, "", "/discover"); });
afterEach(() => { cleanup(); localStorage.clear(); vi.restoreAllMocks(); });

test("searches Open Library and saves a reading status", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return new Response(JSON.stringify(user), { status: 200 });
    if (url.includes("/books/search")) return new Response(JSON.stringify({ total: 1, books: [book] }), { status: 200 });
    if (url.endsWith("/books/library") && init?.method === "PUT") return new Response(JSON.stringify({ id: 1, status: "WANT_TO_READ", rating: null, review: null, book }), { status: 200 });
    return new Response(null, { status: 404 });
  });
  const visitor = userEvent.setup(); render(<App />);
  await screen.findByRole("heading", { name: /discover your next book/i });
  await visitor.type(screen.getByLabelText("Book search"), "test");
  await visitor.click(screen.getByRole("button", { name: "Search" }));
  expect(await screen.findByRole("heading", { name: "The Test Book" })).toBeInTheDocument();
  await visitor.click(screen.getByRole("button", { name: "Save" }));
  expect(await screen.findByText("Saved to your library")).toBeInTheDocument();
  expect(fetchMock.mock.calls.some(([url]) => String(url).includes("field=keyword"))).toBe(true);
});