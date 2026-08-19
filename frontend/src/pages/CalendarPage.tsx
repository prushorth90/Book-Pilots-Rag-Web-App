import type { DateSelectArg } from "@fullcalendar/core";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin, { type DateClickArg } from "@fullcalendar/interaction";
import FullCalendar from "@fullcalendar/react";
import timeGridPlugin from "@fullcalendar/timegrid";
import { useEffect, useState } from "react";

import { getClub, getClubs } from "../api/clubs";
import { getMeetings, getMyAvailability, saveMyAvailability } from "../api/meetings";
import { MeetingDetails } from "../components/MeetingDetails";
import { MeetingForm } from "../components/MeetingForm";
import type { ClubDetail } from "../types/clubs";
import type { Availability, Meeting } from "../types/meetings";

interface Selection { start: string; end: string }

export function CalendarPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [clubs, setClubs] = useState<ClubDetail[]>([]);
  const [range, setRange] = useState({ start: new Date(), end: new Date(Date.now() + 31 * 86_400_000) });
  const [selection, setSelection] = useState<Selection | null>(null);
  const [selected, setSelected] = useState<Meeting | null>(null);
  const [availability, setAvailability] = useState<Availability[]>([]);

  async function refresh() {
    const next = await getMeetings(range.start, range.end); setMeetings(next);
    if (selected) setSelected(next.find((meeting) => meeting.id === selected.id) ?? null);
  }
  useEffect(() => { getClubs().then((items) => Promise.all(items.map((club) => getClub(club.id)))).then(setClubs); getMyAvailability().then(setAvailability); }, []);
  useEffect(() => {
    getMeetings(range.start, range.end).then(setMeetings);
  }, [range]);

  function chooseSlot(start: Date, end: Date) { setSelected(null); setSelection({ start: start.toISOString(), end: end.toISOString() }); }
  function selectSlot(info: DateSelectArg) { chooseSlot(info.start, info.end); }
  function clickDate(info: DateClickArg) { const end = new Date(info.date.getTime() + 60 * 60_000); chooseSlot(info.date, end); }
  async function addAvailability() {
    if (!selection) return;
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const intervals = [...availability.map((item) => ({ start_time: item.start_time, end_time: item.end_time, timezone: item.timezone })), { start_time: selection.start, end_time: selection.end, timezone }];
    setAvailability(await saveMyAvailability(intervals));
  }
  return (
    <section className="calendar-page">
      <div className="calendar-heading"><div><p className="kicker">Club schedule</p><h1>Reading calendar.</h1></div><p>Times shown in {Intl.DateTimeFormat().resolvedOptions().timeZone}</p></div>
      <div className="calendar-layout"><div className="calendar-surface">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth" headerToolbar={{ left: "prev,next today", center: "title", right: "dayGridMonth,timeGridWeek,timeGridDay" }}
          selectable selectMirror nowIndicator height="auto" events={meetings.map((meeting) => ({ id: String(meeting.id), title: meeting.title, start: meeting.start_time, end: meeting.end_time, className: meeting.status === "CANCELLED" ? "cancelled-event" : "" }))}
          datesSet={(info) => setRange({ start: info.start, end: info.end })}
          select={selectSlot} dateClick={clickDate}
          eventClick={(info) => { setSelection(null); setSelected(meetings.find((meeting) => meeting.id === Number(info.event.id)) ?? null); }}
        />
        {selection ? <div className="slot-actions"><span>Selected: {new Date(selection.start).toLocaleString()}–{new Date(selection.end).toLocaleTimeString()}</span><button type="button" onClick={addAvailability}>Mark available</button></div> : null}
      </div>
      {selection ? <MeetingForm clubs={clubs} initialStart={selection.start} initialEnd={selection.end} onClose={() => setSelection(null)} onCreated={() => { setSelection(null); refresh(); }} /> : null}
      {selected ? <MeetingDetails meeting={selected} viewerRole={clubs.find((club) => club.id === selected.club_id)?.viewer_role ?? null} onClose={() => setSelected(null)} onChange={refresh} /> : null}
      </div>
    </section>
  );
}