import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { AuthForm } from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setError(null);
    try {
      await login({ email: String(form.get("email")), password: String(form.get("password")) });
      const destination = (location.state as { from?: string } | null)?.from ?? "/dashboard";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthForm
      eyebrow="Welcome back"
      title="Return to your reading table."
      submitLabel="Sign in"
      alternateText="New to Book Pilots?"
      alternateLabel="Create an account"
      alternateTo="/register"
      error={error}
      submitting={submitting}
      onSubmit={handleSubmit}
    >
      <label>Email<input name="email" type="email" autoComplete="email" required /></label>
      <label>Password<input name="password" type="password" autoComplete="current-password" required /></label>
    </AuthForm>
  );
}