import { useEffect, useState, type FormEvent } from "react";

import { ApiError } from "../api/client";
import { createMeeting, getClubAvailability, getMeetingSuggestions } from "../api/meetings";
import type { ClubDetail } from "../types/clubs";
import type { Availability, SuggestedSlot } from "../types/meetings";

interface Props {
  clubs: ClubDetail[];
  initialStart: string;
  initialEnd: string;
  onCreated: () => void;
  onClose: () => void;
}

function localInput(date: Date): string {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

export function MeetingForm({ clubs, initialStart, initialEnd, onCreated, onClose }: Props) {
  const manageable = clubs.filter((club) => club.viewer_role === "OWNER" || club.viewer_role === "ADMIN");
  const [clubId, setClubId] = useState(manageable[0]?.id ?? 0);
  const [start, setStart] = useState(initialStart);
  const [end, setEnd] = useState(initialEnd);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [invitees, setInvitees] = useState<number[]>([]);
  const [suggestions, setSuggestions] = useState<SuggestedSlot[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    if (!clubId || !start || !end) return;
    getClubAvailability(clubId, new Date(start), new Date(end)).then(setAvailability).catch(() => setAvailability([]));
  }, [clubId, start, end]);
  const selectedClub = manageable.find((club) => club.id === clubId);
  useEffect(() => {
    if (!clubId) return;
    const windowStart = new Date(start);
    const windowEnd = new Date(windowStart.getTime() + 14 * 86_400_000);
    const requestedDuration = Math.round(
      (new Date(end).getTime() - windowStart.getTime()) / 60_000,
    );
    const duration = requestedDuration >= 30 && requestedDuration <= 480 ? requestedDuration : 60;
    getMeetingSuggestions(clubId, windowStart, windowEnd, invitees, duration)
      .then(setSuggestions).catch(() => setSuggestions([]));
  }, [clubId, start, end, invitees]);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    try {
      await createMeeting({
        club_id: clubId,
        title: String(form.get("title")), description: String(form.get("description")) || null,
        start_time: new Date(start).toISOString(), end_time: new Date(end).toISOString(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        location: String(form.get("location")) || null,
        invitee_ids: invitees,
      });
      onCreated();
    } catch (requestError) { setError(requestError instanceof ApiError ? requestError.message : "Could not schedule this meeting. Check the times and your club role."); }
  }
  return (
    <aside className="meeting-form-panel" aria-label="Schedule meeting">
      <button className="panel-close" type="button" onClick={onClose} aria-label="Close meeting form">Close</button>
      <p className="kicker">New club meeting</p><h2>Book a time.</h2>
      {!manageable.length ? <p>You must be a club owner or admin to schedule meetings.</p> : <form onSubmit={submit}>
        <label>Book club<select aria-label="Book club" value={clubId} onChange={(event) => setClubId(Number(event.target.value))}>{manageable.map((club) => <option key={club.id} value={club.id}>{club.name}</option>)}</select></label>
        <label>Title<input name="title" required maxLength={200} /></label>
        <fieldset className="invitee-picker"><legend>Invite members</legend>{selectedClub?.members.filter((member) => member.role !== "OWNER" || member.user.id !== selectedClub.members.find((item) => item.role === "OWNER")?.user.id).map((member) => <label key={member.id}><input type="checkbox" checked={invitees.includes(member.user.id)} onChange={() => setInvitees((current) => current.includes(member.user.id) ? current.filter((id) => id !== member.user.id) : [...current, member.user.id])} />{member.user.first_name} {member.user.last_name}</label>)}</fieldset>
        <div className="field-row"><label>Starts<input aria-label="Starts" type="datetime-local" value={localInput(new Date(start))} onChange={(event) => setStart(new Date(event.target.value).toISOString())} required /></label><label>Ends<input aria-label="Ends" type="datetime-local" value={localInput(new Date(end))} onChange={(event) => setEnd(new Date(event.target.value).toISOString())} required /></label></div>
        <label>Location or video link<input name="location" placeholder="Room 4 or https://..." /></label>
        <label>Description<textarea name="description" /></label>
        <div className="availability-preview"><strong>Available club members in this window</strong>{availability.length ? availability.map((slot) => <span key={slot.id}>{slot.user?.first_name ?? "Member"}: {new Date(slot.start_time).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}–{new Date(slot.end_time).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span>) : <span>No availability has been shared for this window.</span>}</div>
        <div className="suggested-slots"><strong>Suggested times</strong>{suggestions.length ? suggestions.slice(0, 5).map((slot) => <button type="button" key={slot.start_time} onClick={() => { setStart(slot.start_time); setEnd(slot.end_time); }}>{new Date(slot.start_time).toLocaleString([], { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}</button>) : <span>No shared opening found in the next two weeks.</span>}</div>
        {error ? <p role="alert" className="form-error">{error}</p> : null}<button className="form-submit" type="submit">Book meeting</button>
      </form>}
    </aside>
  );
}