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
        <article><BookMarked /><h2>Discover books</h2><p>Search Open Library and build your reading history.</p><Link to="/discover">Start discovering</Link></article>
        <article><Users /><h2>Book clubs</h2><p>Read together, choose club books, and grow a shared reading room.</p><Link to="/clubs">Browse clubs</Link></article>
      </div>
      <Link className="text-link" to="/profile">View profile</Link>
    </section>
  );
}