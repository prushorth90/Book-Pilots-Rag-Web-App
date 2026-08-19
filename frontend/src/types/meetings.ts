import type { User } from "./auth";

export type MeetingStatus = "SCHEDULED" | "CANCELLED";
export type RsvpStatus = "PENDING" | "ACCEPTED" | "DECLINED" | "MAYBE";

export interface MeetingAttendee {
  id: number;
  status: RsvpStatus;
  user: User;
}

export interface Meeting {
  id: number;
  club_id: number;
  club_name: string;
  creator_id: number;
  organizer: User;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  timezone: string;
  location: string | null;
  status: MeetingStatus;
  created_at: string;
  attendees: MeetingAttendee[];
  viewer_rsvp: RsvpStatus | null;
}

export interface MeetingInput {
  club_id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  timezone: string;
  location: string | null;
  invitee_ids: number[];
}

export interface Availability {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string;
  timezone: string;
  user: User | null;
}

export interface WeeklyAvailability {
  id: number;
  user_id: number;
  weekday: number;
  start_minute: number;
  end_minute: number;
  timezone: string;
}

export interface SuggestedSlot {
  start_time: string;
  end_time: string;
  available_user_ids: number[];
}