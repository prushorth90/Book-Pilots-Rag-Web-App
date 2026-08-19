import type { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children }: PropsWithChildren) {
  const { loading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (loading) return <div className="route-loading">Loading your account...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}