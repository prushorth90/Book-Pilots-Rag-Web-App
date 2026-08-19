import { Crown, Shield, UserRound, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Link } from "react-router-dom";

import { changeClubRole, deleteClub, getClub, joinClub, leaveClub, removeClubMember, saveClubBook } from "../api/clubs";
import { getLibrary } from "../api/books";
import { BookCover } from "../components/BookCover";
import { useAuth } from "../context/AuthContext";
import type { Book, LibraryEntry } from "../types/books";
import type { ClubBookStatus, ClubDetail, ClubMember, ClubRole } from "../types/clubs";

const roleIcon = { OWNER: Crown, ADMIN: Shield, MODERATOR: Shield, MEMBER: UserRound };

export function ClubDetailsPage() {
  const { clubId = "" } = useParams();
  const id = Number(clubId);
  const navigate = useNavigate();
  const { user } = useAuth();
  const [club, setClub] = useState<ClubDetail | null>(null);
  const [library, setLibrary] = useState<LibraryEntry[]>([]);
  const [message, setMessage] = useState("");
  const canManage = club?.viewer_role === "OWNER" || club?.viewer_role === "ADMIN";
  useEffect(() => { getClub(id).then(setClub); getLibrary().then(setLibrary).catch(() => setLibrary([])); }, [id]);

  async function join() { await joinClub(id); setClub(await getClub(id)); }
  async function leave() { await leaveClub(id); navigate("/clubs"); }
  async function remove() { if (confirm("Delete this club permanently?")) { await deleteClub(id); navigate("/clubs"); } }
  async function changeRole(member: ClubMember, role: ClubRole) {
    await changeClubRole(id, member.id, role); setClub(await getClub(id));
  }
  async function kick(member: ClubMember) { await removeClubMember(id, member.id); setClub(await getClub(id)); }
  async function setBook(book: Book, status: ClubBookStatus) {
    await saveClubBook(id, book, status); setClub(await getClub(id)); setMessage("Club reading list updated");
  }
  if (!club) return <p className="route-loading">Loading club...</p>;
  const current = club.books.find((item) => item.status === "CURRENT");
  return (
    <section className="club-details-page">
      <header className="club-hero">
        <div><p className="kicker">{club.is_public ? "Public book club" : "Private book club"}</p><h1>{club.name}</h1><p>{club.description ?? "A gathering place for readers."}</p></div>
        <div className="club-actions">
          {club.viewer_role ? <Link to="/calendar">View calendar</Link> : null}
          {!club.viewer_role && club.is_public ? <button onClick={join} type="button">Join club</button> : null}
          {club.viewer_role && club.viewer_role !== "OWNER" ? <button onClick={leave} type="button">Leave club</button> : null}
          {club.viewer_role === "OWNER" ? <button className="danger-action" onClick={remove} type="button">Delete club</button> : null}
        </div>
      </header>

      <div className="club-content-grid">
        <section className="current-reading">
          <p className="section-label">Current book</p>
          {current ? <div className="current-book-display"><BookCover url={current.book.cover_image_url} title={current.book.title} /><div><h2>{current.book.title}</h2><p>{current.book.author}</p></div></div> : <p>No current book has been selected.</p>}
          {canManage && library.length ? <div className="club-book-manager"><h3>Manage reading list</h3>{library.map(({ book }) => <div key={book.open_library_key}><span>{book.title}</span><select aria-label={`Status for ${book.title}`} defaultValue="UPCOMING" onChange={(event) => setBook(book, event.target.value as ClubBookStatus)}><option value="UPCOMING">Upcoming</option><option value="CURRENT">Current</option><option value="COMPLETED">Completed</option></select><button type="button" onClick={() => setBook(book, "UPCOMING")}>Add</button></div>)}</div> : null}
          <span className="save-message" aria-live="polite">{message}</span>
          {club.books.filter((item) => item.status !== "CURRENT").length ? <div className="club-book-history"><h3>Reading queue & history</h3>{club.books.filter((item) => item.status !== "CURRENT").map((item) => <p key={item.id}><strong>{item.book.title}</strong><span>{item.status}</span></p>)}</div> : null}
        </section>

        <section className="club-members">
          <div className="section-heading"><p className="section-label">Members</p><span><Users size={16} /> {club.members.length}</span></div>
          <div className="member-list">{club.members.map((member) => {
            const Icon = roleIcon[member.role];
            const isSelf = member.user.id === user?.id;
            const adminCanManage = club.viewer_role === "ADMIN" && ["MEMBER", "MODERATOR"].includes(member.role);
            const editable = !isSelf && (club.viewer_role === "OWNER" || adminCanManage);
            const roleOptions: ClubRole[] = club.viewer_role === "OWNER" ? ["OWNER", "ADMIN", "MODERATOR", "MEMBER"] : ["MODERATOR", "MEMBER"];
            return <div className="member-row" key={member.id}><Icon size={18} /><div><strong>{member.user.first_name} {member.user.last_name}</strong><span>@{member.user.username}</span></div>{editable ? <><select aria-label={`Role for ${member.user.username}`} value={member.role} onChange={(event) => changeRole(member, event.target.value as ClubRole)}>{roleOptions.map((role) => <option key={role}>{role}</option>)}</select><button type="button" onClick={() => kick(member)}>Remove</button></> : <span className={`role-badge role-${member.role.toLowerCase()}`}>{member.role}</span>}</div>;
          })}</div>
        </section>
      </div>
    </section>
  );
}