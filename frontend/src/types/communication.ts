import type { User } from "./auth";
import type { Book } from "./books";

export interface ChatMessage {
  id: number;
  club_id: number;
  sender_id: number;
  sender: User;
  content: string;
  is_deleted: boolean;
  created_at: string;
  edited_at: string | null;
}

export interface DiscussionPost {
  id: number;
  thread_id: number;
  author_id: number;
  author: User;
  parent_id: number | null;
  content: string;
  is_deleted: boolean;
  created_at: string;
  edited_at: string | null;
}

export interface DiscussionThread {
  id: number;
  club_id: number;
  book_id: number;
  creator_id: number;
  creator: User;
  book: Book;
  title: string;
  created_at: string;
  posts: DiscussionPost[];
}