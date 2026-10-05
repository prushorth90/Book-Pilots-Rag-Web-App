import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = { id: 1, username: "reader", email: "reader@example.com", first_name: "Ada", last_name: "Reader", created_at: "2026-01-01T00:00:00Z" };
const book = { id: 1, open_library_key: "DASH1W", title: "Dashboard Book", author: "D. Writer", description: null, isbn: null, cover_image_url: null, publication_year: 2026, genres: ["Mystery"], average_rating: 4.5 };
const entry = { id: 1, status: "READING", rating: null, review: null, book };
const dashboard = { currently_reading: [entry], want_to_read: [{ ...entry, id: 2, status: "WANT_TO_READ" }], recommendations: [{ book, score: .8, explanation: "Matches your interest in mystery." }], favorite_genres: ["Mystery"], clubs: [{ id: 2, name: "Dashboard Club", role: "OWNER", member_count: 3, current_book: book }], recent_messages: [], upcoming_meetings: [{ id: 4, club_id: 2, club_name: "Dashboard Club", creator_id: 1, organizer: user, title: "Chapter Meeting", description: null, start_time: "2026-08-20T18:00:00Z", end_time: "2026-08-20T19:00:00Z", timezone: "UTC", location: null, status: "SCHEDULED", created_at: "2026-08-01T00:00:00Z", attendees: [], viewer_rsvp: "ACCEPTED" }] };

beforeEach(() => { localStorage.setItem("book-pilots-access-token", "token"); window.history.replaceState({}, "", "/dashboard"); });
afterEach(() => { cleanup(); localStorage.clear(); vi.restoreAllMocks(); });

test("renders the aggregated reading workspace from one dashboard request", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return new Response(JSON.stringify(user), { status: 200 });
    if (url.endsWith("/dashboard")) return new Response(JSON.stringify(dashboard), { status: 200 });
    return new Response(null, { status: 404 });
  });
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Currently reading" })).toBeInTheDocument();
  expect((await screen.findAllByText("Dashboard Book")).length).toBeGreaterThan(0);
  expect(screen.getByText("Chapter Meeting")).toBeInTheDocument();
  expect(screen.getByText("Mystery")).toBeInTheDocument();
  expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith("/dashboard"))).toHaveLength(1);
});