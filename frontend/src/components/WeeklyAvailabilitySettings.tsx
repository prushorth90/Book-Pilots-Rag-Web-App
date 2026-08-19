import { Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";

import { getWeeklyAvailability, saveWeeklyAvailability } from "../api/meetings";
import type { WeeklyAvailability } from "../types/meetings";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
type Rule = Omit<WeeklyAvailability, "id" | "user_id">;

function timeValue(minutes: number): string {
  return `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
}

function minutes(value: string): number {
  const [hours, mins] = value.split(":").map(Number);
  return hours * 60 + mins;
}

export function WeeklyAvailabilitySettings({ onClose }: { onClose: () => void }) {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const [rules, setRules] = useState<Rule[]>([]);
  const [message, setMessage] = useState("");
  useEffect(() => { getWeeklyAvailability().then((items) => setRules(items)); }, []);
  function addRule() { setRules((current) => [...current, { weekday: 0, start_minute: 18 * 60, end_minute: 21 * 60, timezone }]); }
  function updateRule(index: number, patch: Partial<Rule>) { setRules((current) => current.map((rule, position) => position === index ? { ...rule, ...patch } : rule)); }
  async function save() { setRules(await saveWeeklyAvailability(rules)); setMessage("Weekly availability saved"); }
  return (
    <aside className="availability-settings" aria-label="Weekly availability settings">
      <button className="panel-close" type="button" aria-label="Close availability settings" onClick={onClose}><X size={20} /></button>
      <p className="kicker">Recurring schedule</p><h2>Weekly availability.</h2>
      <p>Set the times you are usually free in {timezone}.</p>
      <div className="weekly-rules">{rules.map((rule, index) => <div key={`${rule.weekday}-${index}`}>
        <select aria-label={`Day ${index + 1}`} value={rule.weekday} onChange={(event) => updateRule(index, { weekday: Number(event.target.value) })}>{DAYS.map((day, dayIndex) => <option value={dayIndex} key={day}>{day}</option>)}</select>
        <input aria-label={`Start time ${index + 1}`} type="time" value={timeValue(rule.start_minute)} onChange={(event) => updateRule(index, { start_minute: minutes(event.target.value) })} />
        <span>to</span>
        <input aria-label={`End time ${index + 1}`} type="time" value={timeValue(rule.end_minute)} onChange={(event) => updateRule(index, { end_minute: minutes(event.target.value) })} />
        <button type="button" aria-label={`Remove availability ${index + 1}`} onClick={() => setRules((current) => current.filter((_, position) => position !== index))}><Trash2 size={17} /></button>
      </div>)}</div>
      <button className="add-rule" type="button" onClick={addRule}><Plus size={17} /> Add weekly time</button>
      <button className="form-submit" type="button" onClick={save}>Save availability</button>
      <span className="save-message" aria-live="polite">{message}</span>
    </aside>
  );
}