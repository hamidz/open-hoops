import type { AnalyticsSummary, Job } from "./types";

function defaultApiUrl(): string {
  if (typeof window === "undefined") return "http://localhost:8000";
  return `${window.location.protocol}//${window.location.hostname}:8000`;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || defaultApiUrl();

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail?.detail ?? body.detail ?? body.error ?? message;
    } catch {
      // keep fallback
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function fetchJobs(): Promise<Job[]> {
  return parseResponse<Job[]>(await fetch(`${API_URL}/api/v1/jobs`, { cache: "no-store" }));
}

export async function fetchJob(jobId: string): Promise<Job> {
  return parseResponse<Job>(await fetch(`${API_URL}/api/v1/jobs/${jobId}`, { cache: "no-store" }));
}

export async function fetchAnalytics(jobId: string): Promise<AnalyticsSummary> {
  return parseResponse<AnalyticsSummary>(
    await fetch(`${API_URL}/api/v1/jobs/${jobId}/analytics`, { cache: "no-store" }),
  );
}

export async function deleteJob(jobId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/jobs/${jobId}`, { method: "DELETE" });
  if (!response.ok) throw new Error(`Delete failed (${response.status})`);
}

export { API_URL };
