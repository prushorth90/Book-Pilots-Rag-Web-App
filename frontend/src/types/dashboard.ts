import type { Book, LibraryEntry } from "./books";
import type { ChatMessage } from "./communication";
import type { ClubRole } from "./clubs";
import type { Meeting } from "./meetings";

export interface DashboardRecommendation {
  book: Book;
  score: number;
  explanation: string;
}

export interface DashboardClub {
  id: number;
  name: string;
  role: ClubRole;
  member_count: number;
  current_book: Book | null;
}

export interface DashboardMessage {
  club_name: string;
  message: ChatMessage;
}

export interface DashboardData {
  currently_reading: LibraryEntry[];
  want_to_read: LibraryEntry[];
  recommendations: DashboardRecommendation[];
  favorite_genres: string[];
  clubs: DashboardClub[];
  recent_messages: DashboardMessage[];
  upcoming_meetings: Meeting[];
}