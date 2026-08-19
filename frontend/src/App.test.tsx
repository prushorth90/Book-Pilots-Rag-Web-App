import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { App } from "./App";

afterEach(() => vi.restoreAllMocks());

test("renders the app and reports a healthy backend", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ status: "healthy", database: "connected" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );

  render(<App />);

  expect(screen.getByRole("heading", { name: /find the book/i })).toBeInTheDocument();
  expect(await screen.findByText("All systems ready")).toBeInTheDocument();
  expect(screen.getByText("API healthy · Database connected")).toBeInTheDocument();
});