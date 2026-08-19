import { BookMarked, CalendarClock, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { getMeetings } from "../api/meetings";
import type { Meeting } from "../types/meetings";

export function DashboardPage() {
  const { user } = useAuth();
  const [upcoming, setUpcoming] = useState<Meeting[]>([]);
  useEffect(() => {
    const start = new Date(); const end = new Date(start.getTime() + 30 * 86_400_000);
    getMeetings(start, end, { mine: true }).then((items) => setUpcoming(items.filter((item) => item.status === "SCHEDULED").slice(0, 3))).catch(() => setUpcoming([]));
  }, []);
  return (
    <section className="dashboard-page">
      <p className="kicker">Your reading desk</p>
      <h1>Good to see you, {user?.first_name}.</h1>
      <div className="dashboard-grid">
        <article><BookMarked /><h2>Discover books</h2><p>Search Open Library and build your reading history.</p><Link to="/discover">Start discovering</Link></article>
        <article><Users /><h2>Book clubs</h2><p>Read together, choose club books, and grow a shared reading room.</p><Link to="/clubs">Browse clubs</Link></article>
      </div>
      <section className="upcoming-agenda"><div className="section-heading"><h2><CalendarClock size={22} /> Upcoming meetings</h2><Link to="/calendar">Open calendar</Link></div>{upcoming.length ? upcoming.map((meeting) => <Link className="agenda-item" to="/calendar" key={meeting.id}><time>{new Date(meeting.start_time).toLocaleDateString([], { month: "short", day: "numeric" })}<span>{new Date(meeting.start_time).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span></time><div><strong>{meeting.title}</strong><span>{meeting.club_name}</span></div></Link>) : <p>No upcoming meetings on your calendar.</p>}</section>
      <Link className="text-link" to="/profile">View profile</Link>
    </section>
  );
}