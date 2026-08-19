import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = { id: 1, username: "reader", email: "reader@example.com", first_name: "Ada", last_name: "Reader", created_at: "2026-01-01T00:00:00Z" };
const club = { id: 2, name: "Chat Club", description: null, is_public: true, created_at: "2026-01-01T00:00:00Z", member_count: 1, current_book: null, viewer_role: "MEMBER", members: [], books: [] };
const message = { id: 3, club_id: 2, sender_id: 1, sender: user, content: "Hello readers", is_deleted: false, created_at: "2026-08-18T12:00:00Z", edited_at: null };

class MockWebSocket {
  static OPEN = 1; readyState = 1; onopen: (() => void) | null = null; onmessage = null; onclose = null;
  constructor() { setTimeout(() => this.onopen?.(), 0); }
  send() {} close() {}
}

beforeEach(() => { localStorage.setItem("book-pilots-access-token", "token"); window.history.replaceState({}, "", "/clubs/2/room"); vi.stubGlobal("WebSocket", MockWebSocket); });
afterEach(() => { cleanup(); localStorage.clear(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

test("renders persistent chat and current-book discussion tab", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return new Response(JSON.stringify(user), { status: 200 });
    if (url.endsWith("/clubs/2")) return new Response(JSON.stringify(club), { status: 200 });
    if (url.endsWith("/clubs/2/messages")) return new Response(JSON.stringify([message]), { status: 200 });
    if (url.endsWith("/clubs/2/discussions")) return new Response(JSON.stringify([]), { status: 200 });
    return new Response(null, { status: 404 });
  });
  const visitor = userEvent.setup(); render(<App />);
  expect(await screen.findByText("Hello readers")).toBeInTheDocument();
  expect(screen.getByText("Ada Reader")).toBeInTheDocument();
  await visitor.click(screen.getByRole("tab", { name: "Book discussion" }));
  expect(await screen.findByText(/start a thread/i)).toBeInTheDocument();
});