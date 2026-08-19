import type { AuthResponse, LoginInput, RegisterInput, TokenPair, User } from "../types/auth";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const accessTokenKey = "book-pilots-access-token";
const refreshTokenKey = "book-pilots-refresh-token";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

class ApiClient {
  hasAccessToken(): boolean {
    return Boolean(localStorage.getItem(accessTokenKey));
  }

  setTokens(tokens: TokenPair): void {
    localStorage.setItem(accessTokenKey, tokens.access_token);
    localStorage.setItem(refreshTokenKey, tokens.refresh_token);
  }

  clearTokens(): void {
    localStorage.removeItem(accessTokenKey);
    localStorage.removeItem(refreshTokenKey);
  }

  async get<T>(path: string, signal?: AbortSignal): Promise<T> {
    return this.request<T>(path, { method: "GET", signal });
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: "POST", body: JSON.stringify(body) });
  }

  login(input: LoginInput): Promise<AuthResponse> {
    return this.post<AuthResponse>("/auth/login", input);
  }

  register(input: RegisterInput): Promise<AuthResponse> {
    return this.post<AuthResponse>("/auth/register", input);
  }

  currentUser(signal?: AbortSignal): Promise<User> {
    return this.get<User>("/auth/me", signal);
  }

  private async request<T>(path: string, init: RequestInit, canRefresh = true): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set("Content-Type", "application/json");
    const accessToken = localStorage.getItem(accessTokenKey);
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

    const response = await fetch(`${apiUrl}${path}`, { ...init, headers });
    const refreshToken = localStorage.getItem(refreshTokenKey);
    if (response.status === 401 && canRefresh && refreshToken && path !== "/auth/refresh") {
      try {
        const tokens = await this.request<TokenPair>(
          "/auth/refresh",
          { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) },
          false,
        );
        this.setTokens(tokens);
        return this.request<T>(path, init, false);
      } catch {
        this.clearTokens();
      }
    }

    if (!response.ok) {
      const error = (await response.json().catch(() => null)) as { detail?: string } | null;
      throw new ApiError(response.status, error?.detail ?? "Request failed");
    }
    return response.json() as Promise<T>;
  }
}

export const apiClient = new ApiClient();