import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = { id: 1, username: "reader", email: "reader@example.com", first_name: "Ada", last_name: "Reader", created_at: "2026-01-01T00:00:00Z" };
const summary = { id: 4, name: "Night Readers", description: "Books after dark", is_public: true, created_at: "2026-01-01T00:00:00Z", member_count: 1, current_book: null };
const joined = { id: 7, role: "MEMBER", joined_at: "2026-01-01T00:00:00Z", user };
const detail = { ...summary, member_count: 2, viewer_role: "MEMBER", members: [joined], books: [] };

beforeEach(() => { localStorage.setItem("book-pilots-access-token", "token"); window.history.replaceState({}, "", "/clubs"); });
afterEach(() => { cleanup(); localStorage.clear(); vi.restoreAllMocks(); });

test("browses and joins a public club", async () => {
  let hasJoined = false;
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return new Response(JSON.stringify(user), { status: 200 });
    if (url.endsWith("/books/library")) return new Response(JSON.stringify([]), { status: 200 });
    if (url.endsWith("/clubs") && (!init?.method || init.method === "GET")) return new Response(JSON.stringify([summary]), { status: 200 });
    if (url.endsWith("/clubs/4/join")) { hasJoined = true; return new Response(JSON.stringify(joined), { status: 200 }); }
    if (url.endsWith("/clubs/4")) return new Response(JSON.stringify(hasJoined ? detail : { ...detail, member_count: 1, viewer_role: null, members: [] }), { status: 200 });
    return new Response(null, { status: 404 });
  });
  const visitor = userEvent.setup(); render(<App />);
  expect(await screen.findByRole("heading", { name: "Night Readers" })).toBeInTheDocument();
  await visitor.click(screen.getByRole("link", { name: "Night Readers" }));
  await visitor.click(await screen.findByRole("button", { name: "Join club" }));
  expect(await screen.findByText("MEMBER")).toBeInTheDocument();
  expect(screen.getByText("@reader")).toBeInTheDocument();
});