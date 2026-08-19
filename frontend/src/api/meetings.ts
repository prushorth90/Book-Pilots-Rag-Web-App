import { apiClient } from "./client";
import type { Availability, Meeting, MeetingAttendee, MeetingInput, RsvpStatus } from "../types/meetings";

export function getMeetings(start: Date, end: Date, clubId?: number): Promise<Meeting[]> {
  const params = new URLSearchParams({ start: start.toISOString(), end: end.toISOString() });
  if (clubId) params.set("club_id", String(clubId));
  return apiClient.get<Meeting[]>(`/meetings?${params}`);
}

export function createMeeting(input: MeetingInput): Promise<Meeting> {
  return apiClient.post<Meeting>("/meetings", input);
}

export function updateMeeting(id: number, input: Partial<MeetingInput>): Promise<Meeting> {
  return apiClient.patch<Meeting>(`/meetings/${id}`, input);
}

export function cancelMeeting(id: number): Promise<Meeting> {
  return apiClient.post<Meeting>(`/meetings/${id}/cancel`, {});
}

export function setRsvp(id: number, status: RsvpStatus): Promise<MeetingAttendee> {
  return apiClient.put<MeetingAttendee>(`/meetings/${id}/rsvp`, { status });
}

export function getMyAvailability(): Promise<Availability[]> {
  return apiClient.get<Availability[]>("/availability/me");
}

export function saveMyAvailability(
  intervals: Array<{ start_time: string; end_time: string; timezone: string }>,
): Promise<Availability[]> {
  return apiClient.put<Availability[]>("/availability/me", { intervals });
}

export function getClubAvailability(clubId: number, start: Date, end: Date): Promise<Availability[]> {
  const params = new URLSearchParams({ start: start.toISOString(), end: end.toISOString() });
  return apiClient.get<Availability[]>(`/availability/clubs/${clubId}?${params}`);
}