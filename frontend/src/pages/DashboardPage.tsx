import {
  BookMarked,
  CalendarDays,
  CalendarPlus,
  ChevronRight,
  Compass,
  MessageCircle,
  Plus,
  Sparkles,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboard } from "../api/dashboard";
import { BookCover } from "../components/BookCover";
import { useAuth } from "../context/AuthContext";
import type { DashboardData } from "../types/dashboard";

const EMPTY_DASHBOARD: DashboardData = {
  currently_reading: [],
  want_to_read: [],
  recommendations: [],
  favorite_genres: [],
  clubs: [],
  recent_messages: [],
  upcoming_meetings: [],
};

export function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData>(EMPTY_DASHBOARD);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    getDashboard().then(setData).catch(() => setData(EMPTY_DASHBOARD)).finally(() => setLoading(false));
  }, []);
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(); date.setHours(0, 0, 0, 0); date.setDate(date.getDate() + index); return date;
  });
  return (
    <section className="dashboard-page">
      <header className="dashboard-header"><div><p className="kicker">Your reading desk</p><h1>Good to see you, {user?.first_name}.</h1></div><p>{loading ? "Gathering your books and clubs..." : `${data.currently_reading.length} in progress · ${data.upcoming_meetings.length} meetings ahead`}</p></header>

      <nav className="quick-actions" aria-label="Dashboard quick actions">
        <Link to="/discover"><Compass size={19} /><span>Search Books</span></Link>
        <a href="#recommendations"><Sparkles size={19} /><span>View Recommendations</span></a>
        <Link to="/clubs/new"><Plus size={19} /><span>Create Book Club</span></Link>
        <Link to="/calendar?schedule=true"><CalendarPlus size={19} /><span>Schedule Meeting</span></Link>
        <Link to="/calendar"><CalendarDays size={19} /><span>Open Calendar</span></Link>
      </nav>

      <div className="dashboard-columns">
        <div className="dashboard-primary">
          <section className="dashboard-section"><div className="dashboard-section-heading"><div><BookMarked size={20} /><h2>Currently reading</h2></div><Link to="/library">Your library</Link></div>
            {data.currently_reading.length ? <div className="reading-strip">{data.currently_reading.slice(0, 4).map((entry) => <Link to={`/books/${entry.book.open_library_key}`} className="dashboard-book" key={entry.id}><BookCover url={entry.book.cover_image_url} title={entry.book.title} /><div><strong>{entry.book.title}</strong><span>{entry.book.author}</span></div></Link>)}</div> : <p className="dashboard-empty">No book in progress. Choose one from your reading list.</p>}
          </section>

          <section className="dashboard-section" id="recommendations"><div className="dashboard-section-heading"><div><Sparkles size={20} /><h2>Recommended for you</h2></div><Link to="/discover">Explore more</Link></div>
            {data.recommendations.length ? <div className="recommendation-strip">{data.recommendations.slice(0, 3).map((item) => <Link to={`/books/${item.book.open_library_key}`} className="recommendation-item" key={item.book.open_library_key}><BookCover url={item.book.cover_image_url} title={item.book.title} /><div><strong>{item.book.title}</strong><span>{item.book.author}</span><p>{item.explanation}</p></div></Link>)}</div> : <p className="dashboard-empty">Rate books and choose favorite genres to unlock recommendations.</p>}
          </section>

          <section className="dashboard-section"><div className="dashboard-section-heading"><div><Users size={20} /><h2>Your book clubs</h2></div><Link to="/clubs">Browse clubs</Link></div>
            {data.clubs.length ? <div className="dashboard-clubs">{data.clubs.slice(0, 4).map((club) => <Link to={`/clubs/${club.id}`} key={club.id}><div><strong>{club.name}</strong><span>{club.role} · {club.member_count} members</span></div><div className="club-reading-now">{club.current_book ? <><span>Current book</span><strong>{club.current_book.title}</strong></> : <span>Choosing a book</span>}</div><ChevronRight size={18} /></Link>)}</div> : <p className="dashboard-empty">You have not joined a book club yet.</p>}
          </section>

          <section className="dashboard-section"><div className="dashboard-section-heading"><div><MessageCircle size={20} /><h2>Recent messages</h2></div></div>
            {data.recent_messages.length ? <div className="recent-message-list">{data.recent_messages.map(({ club_name, message }) => <Link to={`/clubs/${message.club_id}/room?tab=chat`} key={message.id}><div className="message-initial">{message.sender.first_name.charAt(0)}{message.sender.last_name.charAt(0)}</div><div><strong>{message.sender.first_name} {message.sender.last_name}<span> in {club_name}</span></strong><p>{message.content}</p></div><time>{new Date(message.created_at).toLocaleDateString([], { month: "short", day: "numeric" })}</time></Link>)}</div> : <p className="dashboard-empty">Club conversations will appear here.</p>}
          </section>
        </div>

        <aside className="dashboard-sidebar">
          <section className="dashboard-panel meetings-panel"><div className="dashboard-section-heading"><div><CalendarDays size={20} /><h2>Upcoming meetings</h2></div><Link to="/calendar">Calendar</Link></div>
            {data.upcoming_meetings.length ? data.upcoming_meetings.slice(0, 4).map((meeting) => <article className="dashboard-meeting" key={meeting.id}><time><strong>{new Date(meeting.start_time).toLocaleDateString([], { month: "short", day: "numeric" })}</strong><span>{new Date(meeting.start_time).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span></time><div><h3>{meeting.title}</h3><p>{meeting.club_name}</p><span className={`dashboard-rsvp rsvp-${(meeting.viewer_rsvp ?? "PENDING").toLowerCase()}`}>{meeting.viewer_rsvp ?? "PENDING"}</span></div><Link aria-label={`Open ${meeting.title} details`} to={`/calendar?meeting=${meeting.id}`}><ChevronRight size={18} /></Link></article>) : <p className="dashboard-empty">Nothing scheduled in the next 30 days.</p>}
          </section>

          <section className="dashboard-panel mini-calendar"><div className="dashboard-section-heading"><div><CalendarDays size={20} /><h2>Next seven days</h2></div></div><div className="mini-calendar-grid">{days.map((day) => { const count = data.upcoming_meetings.filter((meeting) => new Date(meeting.start_time).toDateString() === day.toDateString()).length; return <div className={count ? "has-event" : ""} key={day.toISOString()}><span>{day.toLocaleDateString([], { weekday: "short" })}</span><strong>{day.getDate()}</strong>{count ? <i>{count}</i> : null}</div>; })}</div></section>

          <section className="dashboard-panel"><div className="dashboard-section-heading"><div><BookMarked size={20} /><h2>Want to read</h2></div><Link to="/library">All</Link></div>{data.want_to_read.length ? <div className="want-list">{data.want_to_read.slice(0, 4).map((entry) => <Link to={`/books/${entry.book.open_library_key}`} key={entry.id}><strong>{entry.book.title}</strong><span>{entry.book.author}</span></Link>)}</div> : <p className="dashboard-empty">Your reading queue is empty.</p>}</section>

          <section className="dashboard-panel"><div className="dashboard-section-heading"><div><Sparkles size={20} /><h2>Favorite genres</h2></div><Link to="/preferences">Edit</Link></div><div className="dashboard-genres">{data.favorite_genres.length ? data.favorite_genres.map((genre) => <span key={genre}>{genre}</span>) : <p className="dashboard-empty">Choose your genres.</p>}</div></section>
        </aside>
      </div>
    </section>
  );
}