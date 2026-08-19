import { useEffect, useState } from "react";

import { getPreferences, savePreferences } from "../api/books";

const GENRES = ["Biography", "Classics", "Fantasy", "Historical fiction", "Horror", "Mystery", "Nonfiction", "Poetry", "Romance", "Science", "Science fiction", "Thriller", "Young adult"];

export function PreferencesPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  useEffect(() => { getPreferences().then(({ genres }) => setSelected(genres)).catch(() => setSelected([])); }, []);
  function toggle(genre: string) { setSelected((current) => current.includes(genre) ? current.filter((item) => item !== genre) : [...current, genre]); }
  async function save() { const result = await savePreferences(selected); setSelected(result.genres); setMessage("Preferences saved"); }
  return (
    <section className="preferences-page">
      <p className="kicker">Recommendation signals</p><h1>What do you love to read?</h1>
      <p>Select the genres you want your future recommendations to understand.</p>
      <div className="genre-picker">{GENRES.map((genre) => <label key={genre}><input type="checkbox" checked={selected.includes(genre)} onChange={() => toggle(genre)} /><span>{genre}</span></label>)}</div>
      <button className="form-submit" type="button" onClick={save}>Save preferences</button><span aria-live="polite">{message}</span>
    </section>
  );
}