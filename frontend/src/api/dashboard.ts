import { apiClient } from "./client";
import type { DashboardData } from "../types/dashboard";

export function getDashboard(): Promise<DashboardData> {
  return apiClient.get<DashboardData>("/dashboard");
}