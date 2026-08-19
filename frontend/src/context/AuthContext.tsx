import {
  createContext,
  startTransition,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";

import { apiClient } from "../api/client";
import type { LoginInput, RegisterInput, User } from "../types/auth";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (input: LoginInput) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [hasStoredToken] = useState(() => apiClient.hasAccessToken());
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(hasStoredToken);

  useEffect(() => {
    if (!hasStoredToken) return;
    const controller = new AbortController();
    apiClient
      .currentUser(controller.signal)
      .then(setUser)
      .catch(() => apiClient.clearTokens())
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [hasStoredToken]);

  async function login(input: LoginInput): Promise<void> {
    const response = await apiClient.login(input);
    apiClient.setTokens(response);
    setUser(response.user);
  }

  async function register(input: RegisterInput): Promise<void> {
    const response = await apiClient.register(input);
    apiClient.setTokens(response);
    setUser(response.user);
  }

  function logout(): void {
    apiClient.clearTokens();
    startTransition(() => setUser(null));
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: Boolean(user), login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}