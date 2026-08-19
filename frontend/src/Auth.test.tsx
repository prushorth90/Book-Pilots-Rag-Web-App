import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const user = {
  id: 1,
  username: "reader_one",
  email: "reader@example.com",
  first_name: "Ada",
  last_name: "Reader",
  created_at: "2026-08-18T00:00:00Z",
};
const authResponse = {
  user,
  access_token: "access-token",
  refresh_token: "refresh-token",
  token_type: "bearer",
};

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  window.history.replaceState({}, "", "/");
});

test("registers a user and opens the protected dashboard", async () => {
  window.history.replaceState({}, "", "/register");
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify(authResponse), { status: 201 }),
  );
  const visitor = userEvent.setup();
  render(<App />);

  await visitor.type(screen.getByLabelText("First name"), "Ada");
  await visitor.type(screen.getByLabelText("Last name"), "Reader");
  await visitor.type(screen.getByLabelText("Username"), "reader_one");
  await visitor.type(screen.getByLabelText("Email"), "reader@example.com");
  await visitor.type(screen.getByLabelText("Password"), "correct-horse-battery");
  await visitor.click(screen.getByRole("button", { name: "Create account" }));

  expect(await screen.findByRole("heading", { name: /good to see you, ada/i })).toBeInTheDocument();
  expect(localStorage.getItem("book-pilots-access-token")).toBe("access-token");
});

test("logs in and displays invalid credentials", async () => {
  window.history.replaceState({}, "", "/login");
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ detail: "Invalid email or password" }), { status: 401 }),
  );
  const visitor = userEvent.setup();
  render(<App />);

  await visitor.type(screen.getByLabelText("Email"), "reader@example.com");
  await visitor.type(screen.getByLabelText("Password"), "wrong-password");
  await visitor.click(screen.getByRole("button", { name: "Sign in" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Invalid email or password");
});

test("redirects anonymous visitors away from protected routes", async () => {
  window.history.replaceState({}, "", "/dashboard");
  render(<App />);

  expect(await screen.findByRole("heading", { name: /return to your reading table/i })).toBeInTheDocument();
});

test("restores a session, attaches its token, and logs out", async () => {
  localStorage.setItem("book-pilots-access-token", "access-token");
  localStorage.setItem("book-pilots-refresh-token", "refresh-token");
  window.history.replaceState({}, "", "/dashboard");
  const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify(user), { status: 200 }),
  );
  const visitor = userEvent.setup();
  render(<App />);

  expect(await screen.findByRole("heading", { name: /good to see you, ada/i })).toBeInTheDocument();
  expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get("Authorization")).toBe("Bearer access-token");
  await visitor.click(screen.getByRole("link", { name: "Log out" }));

  expect(await screen.findByRole("heading", { name: /find the book/i })).toBeInTheDocument();
  expect(localStorage.getItem("book-pilots-access-token")).toBeNull();
});