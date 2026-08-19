import { BookOpen, LockKeyhole, Users } from "lucide-react";
import { Link } from "react-router-dom";

import type { ClubSummary } from "../types/clubs";

export function ClubCard({ club }: { club: ClubSummary }) {
  return (
    <article className="club-card">
      <div className="club-card-meta">
        <span><Users size={15} /> {club.member_count}</span>
        <span>{club.is_public ? "Public" : <><LockKeyhole size={14} /> Private</>}</span>
      </div>
      <h2><Link to={`/clubs/${club.id}`}>{club.name}</Link></h2>
      <p>{club.description ?? "A gathering place for readers."}</p>
      <div className="club-current-book">
        <BookOpen size={17} />
        <span>{club.current_book ? `Reading ${club.current_book.title}` : "Choosing the next book"}</span>
      </div>
    </article>
  );
}