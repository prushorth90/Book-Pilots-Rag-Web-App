import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = { id: 1, username: "owner", email: "owner@example.com", first_name: "Club", last_name: "Owner", created_at: "2026-01-01T00:00:00Z" };
const club = { id: 2, name: "Calendar Club", description: null, is_public: true, created_at: "2026-01-01T00:00:00Z", member_count: 1, current_book: null, viewer_role: "OWNER", members: [], books: [] };
const meeting = { id: 3, club_id: 2, club_name: "Calendar Club", creator_id: 1, organizer: user, title: "Chapter discussion", description: "Discuss chapters", start_time: "2026-08-20T18:00:00Z", end_time: "2026-08-20T19:00:00Z", timezone: "UTC", location: "Room 4", status: "SCHEDULED", created_at: "2026-08-01T00:00:00Z", attendees: [{ id: 1, status: "ACCEPTED", user }], viewer_rsvp: "ACCEPTED" };

beforeEach(() => { localStorage.setItem("book-pilots-access-token", "token"); window.history.replaceState({}, "", "/calendar"); });
afterEach(() => { cleanup(); localStorage.clear(); vi.restoreAllMocks(); });

test("renders club meetings and opens attendee details", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return new Response(JSON.stringify(user), { status: 200 });
    if (url.endsWith("/clubs")) return new Response(JSON.stringify([club]), { status: 200 });
    if (url.endsWith("/clubs/2")) return new Response(JSON.stringify(club), { status: 200 });
    if (url.includes("/meetings?")) return new Response(JSON.stringify([meeting]), { status: 200 });
    if (url.endsWith("/availability/me")) return new Response(JSON.stringify([]), { status: 200 });
    return new Response(null, { status: 404 });
  });
  const visitor = userEvent.setup(); render(<App />);
  await visitor.click(await screen.findByText("Chapter discussion"));
  expect(await screen.findByRole("heading", { name: "Chapter discussion" })).toBeInTheDocument();
  expect(screen.getAllByText("Club Owner").length).toBeGreaterThan(0);
  expect(screen.getByText("Room 4")).toBeInTheDocument();
  expect(screen.getAllByText("ACCEPTED").length).toBeGreaterThan(0);
});