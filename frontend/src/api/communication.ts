import { apiClient } from "./client";
import type { ChatMessage, DiscussionPost, DiscussionThread } from "../types/communication";

export function getMessageHistory(clubId: number): Promise<ChatMessage[]> {
  return apiClient.get<ChatMessage[]>(`/clubs/${clubId}/messages`);
}

export function editMessage(clubId: number, messageId: number, content: string): Promise<ChatMessage> {
  return apiClient.patch<ChatMessage>(`/clubs/${clubId}/messages/${messageId}`, { content });
}

export function deleteMessage(clubId: number, messageId: number): Promise<void> {
  return apiClient.delete(`/clubs/${clubId}/messages/${messageId}`);
}

export function moderateMessage(clubId: number, messageId: number): Promise<ChatMessage> {
  return apiClient.post<ChatMessage>(`/clubs/${clubId}/moderation/messages/${messageId}`, {});
}

export function getDiscussions(clubId: number): Promise<DiscussionThread[]> {
  return apiClient.get<DiscussionThread[]>(`/clubs/${clubId}/discussions`);
}

export function createDiscussion(clubId: number, title: string): Promise<DiscussionThread> {
  return apiClient.post<DiscussionThread>(`/clubs/${clubId}/discussions`, { title });
}

export function createDiscussionPost(
  clubId: number,
  threadId: number,
  content: string,
  parentId: number | null = null,
): Promise<DiscussionPost> {
  return apiClient.post<DiscussionPost>(`/clubs/${clubId}/discussions/${threadId}/posts`, {
    content,
    parent_id: parentId,
  });
}

export function deleteDiscussionPost(clubId: number, postId: number): Promise<void> {
  return apiClient.delete(`/clubs/${clubId}/discussions/posts/${postId}`);
}

export function clubChatUrl(clubId: number): string {
  const url = new URL(apiClient.websocketUrl(`/ws/clubs/${clubId}`));
  url.searchParams.set("token", apiClient.getAccessToken() ?? "");
  return url.toString();
}