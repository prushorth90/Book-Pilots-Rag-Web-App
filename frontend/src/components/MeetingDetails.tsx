import { CalendarClock, MapPin, Users, X } from "lucide-react";
import { Link } from "react-router-dom";

import { cancelMeeting, setRsvp } from "../api/meetings";
import type { ClubRole } from "../types/clubs";
import type { Meeting, RsvpStatus } from "../types/meetings";

interface Props {
  meeting: Meeting;
  viewerRole: ClubRole | null;
  onClose: () => void;
  onChange: () => void;
}

export function MeetingDetails({ meeting, viewerRole, onClose, onChange }: Props) {
  const canManage = viewerRole === "OWNER" || viewerRole === "ADMIN";
  const format = (value: string) => new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium", timeStyle: "short",
  }).format(new Date(value));
  async function rsvp(status: RsvpStatus) { await setRsvp(meeting.id, status); onChange(); }
  async function cancel() { await cancelMeeting(meeting.id); onChange(); }
  return (
    <aside className="meeting-details" aria-label="Meeting details">
      <button className="panel-close" type="button" aria-label="Close meeting details" onClick={onClose}><X size={20} /></button>
      <p className="kicker">{meeting.club_name}</p><h2>{meeting.title}</h2>
      <div className="meeting-room-links"><Link to={`/clubs/${meeting.club_id}/room?tab=chat`}>Open club chat</Link><Link to={`/clubs/${meeting.club_id}/room?tab=discussion`}>Book discussion</Link></div>
      <span className={`meeting-status status-${meeting.status.toLowerCase()}`}>{meeting.status}</span>
      <div className="meeting-detail-row"><CalendarClock size={18} /><span>{format(meeting.start_time)}<br />to {format(meeting.end_time)}</span></div>
      {meeting.location ? <div className="meeting-detail-row"><MapPin size={18} />{meeting.location.startsWith("http") ? <a href={meeting.location} target="_blank" rel="noreferrer">Join meeting</a> : <span>{meeting.location}</span>}</div> : null}
      <p>{meeting.description ?? "No meeting notes."}</p>
      <div className="organizer-line"><strong>Organizer</strong><span>{meeting.organizer.first_name} {meeting.organizer.last_name}</span></div>
      <div className="attendee-section"><h3><Users size={17} /> Attendees</h3>{meeting.attendees.length ? meeting.attendees.map((attendee) => <p key={attendee.id}><span>{attendee.user.first_name} {attendee.user.last_name}</span><strong>{attendee.status}</strong></p>) : <p>No responses yet.</p>}</div>
      {meeting.status !== "CANCELLED" ? <div className="rsvp-actions"><span>Your RSVP</span>{(["ACCEPTED", "MAYBE", "DECLINED"] as RsvpStatus[]).map((status) => <button className={meeting.viewer_rsvp === status ? "active" : ""} type="button" key={status} onClick={() => rsvp(status)}>{status}</button>)}</div> : null}
      {canManage && meeting.status !== "CANCELLED" ? <button className="cancel-meeting" type="button" onClick={cancel}>Cancel meeting</button> : null}
    </aside>
  );
}