import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { AuthForm } from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setError(null);
    try {
      await register({
        username: String(form.get("username")),
        email: String(form.get("email")),
        password: String(form.get("password")),
        first_name: String(form.get("first_name")),
        last_name: String(form.get("last_name")),
      });
      navigate("/dashboard", { replace: true });
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Unable to register");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthForm
      eyebrow="Join the club"
      title="Begin your next reading chapter."
      submitLabel="Create account"
      alternateText="Already have an account?"
      alternateLabel="Sign in"
      alternateTo="/login"
      error={error}
      submitting={submitting}
      onSubmit={handleSubmit}
    >
      <div className="field-row">
        <label>First name<input name="first_name" autoComplete="given-name" required /></label>
        <label>Last name<input name="last_name" autoComplete="family-name" required /></label>
      </div>
      <label>Username<input name="username" minLength={3} autoComplete="username" required /></label>
      <label>Email<input name="email" type="email" autoComplete="email" required /></label>
      <label>Password<input name="password" type="password" minLength={8} autoComplete="new-password" required /></label>
    </AuthForm>
  );
}