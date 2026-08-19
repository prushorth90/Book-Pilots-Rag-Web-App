import { useEffect, useState } from "react";

import { getHealth } from "../api/health";
import type { HealthResponse } from "../types/health";

type HealthState =
  | { kind: "loading" }
  | { kind: "ready"; health: HealthResponse }
  | { kind: "error" };

export function useHealth(): HealthState {
  const [state, setState] = useState<HealthState>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    getHealth(controller.signal)
      .then((health) => setState({ kind: "ready", health }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setState({ kind: "error" });
      });
    return () => controller.abort();
  }, []);

  return state;
}