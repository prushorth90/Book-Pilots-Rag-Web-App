import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { createClub } from "../api/clubs";

export function CreateClubPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const club = await createClub({
        name: String(form.get("name")),
        description: String(form.get("description")) || null,
        is_public: form.get("is_public") === "on",
      });
      navigate(`/clubs/${club.id}`, { replace: true });
    } catch { setError("Could not create this club. The name may already be in use."); }
  }
  return (
    <section className="create-club-page">
      <div><p className="kicker">Gather your readers</p><h1>Create a book club.</h1><p>Choose a clear purpose, invite members, and set the first reading selection.</p></div>
      <form className="account-form" onSubmit={submit}>
        <label>Club name<input name="name" minLength={3} maxLength={150} required /></label>
        <label>Description<textarea name="description" maxLength={5000} /></label>
        <label className="visibility-toggle"><input name="is_public" type="checkbox" defaultChecked /><span>Public club</span></label>
        {error ? <p className="form-error" role="alert">{error}</p> : null}
        <button className="form-submit" type="submit">Create club</button>
      </form>
    </section>
  );
}