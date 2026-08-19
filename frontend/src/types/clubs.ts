import type { User } from "./auth";
import type { Book } from "./books";

export type ClubRole = "OWNER" | "ADMIN" | "MODERATOR" | "MEMBER";
export type ClubBookStatus = "CURRENT" | "UPCOMING" | "COMPLETED";

export interface ClubSummary {
  id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  member_count: number;
  current_book: Book | null;
}

export interface ClubMember {
  id: number;
  role: ClubRole;
  joined_at: string;
  user: User;
}

export interface ClubBook {
  id: number;
  status: ClubBookStatus;
  book: Book;
}

export interface ClubDetail extends ClubSummary {
  members: ClubMember[];
  books: ClubBook[];
  viewer_role: ClubRole | null;
}

export interface ClubInput {
  name: string;
  description: string | null;
  is_public: boolean;
}