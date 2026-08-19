import { apiClient } from "./client";
import type { Book } from "../types/books";
import type { ClubBook, ClubBookStatus, ClubDetail, ClubInput, ClubMember, ClubRole, ClubSummary } from "../types/clubs";

export function getClubs(): Promise<ClubSummary[]> {
  return apiClient.get<ClubSummary[]>("/clubs");
}

export function getClub(id: number): Promise<ClubDetail> {
  return apiClient.get<ClubDetail>(`/clubs/${id}`);
}

export function createClub(input: ClubInput): Promise<ClubDetail> {
  return apiClient.post<ClubDetail>("/clubs", input);
}

export function updateClub(id: number, input: Partial<ClubInput>): Promise<ClubDetail> {
  return apiClient.patch<ClubDetail>(`/clubs/${id}`, input);
}

export function deleteClub(id: number): Promise<void> {
  return apiClient.delete(`/clubs/${id}`);
}

export function joinClub(id: number): Promise<ClubMember> {
  return apiClient.post<ClubMember>(`/clubs/${id}/join`, {});
}

export function leaveClub(id: number): Promise<void> {
  return apiClient.delete(`/clubs/${id}/leave`);
}

export function changeClubRole(clubId: number, memberId: number, role: ClubRole): Promise<ClubMember> {
  return apiClient.patch<ClubMember>(`/clubs/${clubId}/members/${memberId}`, { role });
}

export function removeClubMember(clubId: number, memberId: number): Promise<void> {
  return apiClient.delete(`/clubs/${clubId}/members/${memberId}`);
}

export function saveClubBook(clubId: number, book: Book, status: ClubBookStatus): Promise<ClubBook> {
  return apiClient.put<ClubBook>(`/clubs/${clubId}/books`, { book, status });
}