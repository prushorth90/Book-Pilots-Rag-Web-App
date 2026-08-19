import { Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getClubs } from "../api/clubs";
import { ClubCard } from "../components/ClubCard";
import type { ClubSummary } from "../types/clubs";

export function ClubsPage() {
  const [clubs, setClubs] = useState<ClubSummary[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { getClubs().then(setClubs).finally(() => setLoading(false)); }, []);
  return (
    <section className="clubs-page">
      <div className="page-heading-row">
        <div><p className="kicker">Shared reading rooms</p><h1>Book clubs.</h1></div>
        <Link className="create-club-link" to="/clubs/new"><Plus size={18} /> Create club</Link>
      </div>
      {loading ? <p>Loading clubs...</p> : null}
      {!loading && !clubs.length ? <p>No clubs yet. Start the first one.</p> : null}
      <div className="club-grid">{clubs.map((club) => <ClubCard club={club} key={club.id} />)}</div>
    </section>
  );
}