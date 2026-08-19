import { BookMarked, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();
  return (
    <section className="dashboard-page">
      <p className="kicker">Your reading desk</p>
      <h1>Good to see you, {user?.first_name}.</h1>
      <div className="dashboard-grid">
        <article><BookMarked /><h2>Recommendations</h2><p>Your next set of tailored books will appear here.</p></article>
        <article><Users /><h2>Book clubs</h2><p>Your shared reading rooms will appear here.</p></article>
      </div>
      <Link className="text-link" to="/profile">View profile</Link>
    </section>
  );
}