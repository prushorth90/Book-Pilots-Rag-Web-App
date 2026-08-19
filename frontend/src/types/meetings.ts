import type { User } from "./auth";

export type MeetingStatus = "SCHEDULED" | "CANCELLED";
export type RsvpStatus = "GOING" | "MAYBE" | "DECLINED";

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
}

export interface Availability {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string;
  timezone: string;
  user: User | null;
}