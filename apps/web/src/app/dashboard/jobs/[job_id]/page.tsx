"use client";

import Link from "next/link";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { deleteJob, fetchAnalytics, fetchJob } from "@/lib/api";
import { Card, Shell, Stat, StatusBadge } from "@/components/ui";
import CourtSVG from "@/components/court/CourtSVG";
import FrameScrubber from "@/components/court/FrameScrubber";
import ZoneBar from "@/components/analytics/ZoneBar";
import type { PlayerAnalytics } from "@/lib/types";

// ─── Track colour (12-colour palette for dark bg) ─────────────────────────────
const TRACK_COLORS: Record<number, string> = {
  1: "#60A5FA", 2: "#F87171", 3: "#34D399", 4: "#FBBF24",
  5: "#A78BFA", 6: "#FB923C", 7: "#38BDF8", 8: "#F472B6",
  9: "#A3E635", 10: "#E879F9", 11: "#94A3B8", 12: "#FCD34D",
};
function trackColor(id: number) { return TRACK_COLORS[id] ?? "#94A3B8"; }
function teamColor(team: string) { return team === "home" ? "#37d67a" : "#7dd3fc"; }

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-panel-soft ${className}`} />;
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
type Tab = "overview" | "court" | "players" | "report";
const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "court", label: "Court Map" },
  { id: "players", label: "Players" },
  { id: "report", label: "Report" },
];

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function JobDetailPage() {
  const params = useParams<{ job_id: string }>();
  const jobId = params.job_id;
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [frame, setFrame] = useState(0);

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "complete" || status === "failed" ? false : 3000;
    },
  });

  const analyticsQuery = useQuery({
    queryKey: ["analytics", jobId],
    queryFn: () => fetchAnalytics(jobId),
    enabled: jobQuery.data?.status === "complete",
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteJob(jobId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      router.push("/dashboard");
    },
  });

  const job = jobQuery.data;
  const analytics = analyticsQuery.data;

  return (
    <Shell>
      <Link href="/dashboard" className="text-sm text-accent">← Back to dashboard</Link>

      {/* ── Loading skeleton ── */}
      {jobQuery.isLoading && (
        <div className="mt-6 space-y-4">
          <Skeleton className="h-10 w-80" />
          <Skeleton className="h-4 w-56" />
          <Skeleton className="h-3 w-full" />
        </div>
      )}

      {jobQuery.error && (
        <Card className="mt-6 text-danger">
          Could not load job: {(jobQuery.error as Error).message}
        </Card>
      )}

      {job && (
        <>
          {/* ── Job header ── */}
          <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-4xl font-black">{job.label ?? job.original_filename}</h1>
                <StatusBadge status={job.status} />
              </div>
              <p className="mt-2 text-sm text-foreground/70">
                {job.original_filename} ·{" "}
                {(job.file_size_bytes / 1024 / 1024).toFixed(2)} MB ·{" "}
                uploaded {new Date(job.created_at).toLocaleString()}
              </p>
            </div>
            {job.status !== "processing" && (
              <button
                className="rounded-full border border-danger px-4 py-2 text-sm font-bold text-danger disabled:opacity-50"
                disabled={deleteMutation.isPending}
                onClick={() => { if (confirm("Delete this job?")) deleteMutation.mutate(); }}
              >
                {deleteMutation.isPending ? "Deleting…" : "Delete"}
              </button>
            )}
          </div>

          {/* ── Progress bar ── */}
          <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-panel">
            <div className="h-full bg-accent transition-all" style={{ width: `${job.progress_pct}%` }} />
          </div>

          {/* ── Contextual alerts ── */}
          {job.status === "calibration_needed" && (
            <Card className="mt-4">
              Court calibration required before processing.{" "}
              <Link className="font-semibold text-accent" href={`/dashboard/jobs/${job.job_id}/calibrate`}>
                Calibrate now →
              </Link>
            </Card>
          )}
          {job.status === "failed" && (
            <Card className="mt-4 text-danger">{job.error_message ?? "Job failed."}</Card>
          )}
          {deleteMutation.error && (
            <Card className="mt-4 text-danger">Delete failed: {(deleteMutation.error as Error).message}</Card>
          )}

          {/* ── Tab bar ── */}
          <div className="mt-6 flex gap-1 border-b border-line/60 pb-0">
            {TABS.map(({ id, label }) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                className={`rounded-t-lg px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === id
                    ? "border border-b-panel border-line/60 bg-panel text-foreground"
                    : "text-foreground/50 hover:text-foreground"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* ── Tab: Overview ── */}
          {activeTab === "overview" && (
            <div className="mt-6">
              {analyticsQuery.isLoading && (
                <div className="grid gap-4 md:grid-cols-4">
                  {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
                </div>
              )}
              {analytics && (
                <>
                  <div className="grid gap-4 md:grid-cols-4">
                    <Stat label="Players" value={analytics.players.length} />
                    <Stat label="Duration" value={`${Math.round(analytics.duration_seconds / 60)} min`} />
                    <Stat label="Team spacing" value={`${analytics.team_spacing_avg_m} m`} />
                    <Stat label="Ball coverage" value={`${analytics.ball_tracking_coverage_pct}%`} />
                  </div>

                  <Card className="mt-6 overflow-x-auto">
                    <h2 className="mb-4 text-xl font-bold">Player Stats</h2>
                    <table className="w-full min-w-[680px] text-left text-sm">
                      <thead className="text-foreground/60">
                        <tr>
                          <th className="py-2 pr-4">Track</th>
                          <th className="pr-4">Team</th>
                          <th className="pr-4">Distance</th>
                          <th className="pr-4">Avg speed</th>
                          <th className="pr-4">Max speed</th>
                          <th className="pr-4">Coverage</th>
                          <th>Zones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.players.map((p: PlayerAnalytics) => (
                          <tr key={p.track_id} className="border-t border-line/60">
                            <td className="py-3 pr-4">
                              <span
                                className="inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-black"
                                style={{ backgroundColor: trackColor(p.track_id) }}
                              >
                                {p.track_id}
                              </span>
                            </td>
                            <td className="pr-4">
                              <span className="rounded-full px-2 py-0.5 text-xs font-bold"
                                style={{ backgroundColor: `${teamColor(p.team)}20`, color: teamColor(p.team) }}>
                                {p.team}
                              </span>
                            </td>
                            <td className="pr-4 font-mono tabular-nums">{p.total_distance_m} m</td>
                            <td className="pr-4 font-mono tabular-nums">{p.avg_speed_ms} m/s</td>
                            <td className="pr-4 font-mono tabular-nums">{p.max_speed_ms} m/s</td>
                            <td className="pr-4 font-mono tabular-nums">{p.court_coverage_pct}%</td>
                            <td className="min-w-[120px]">
                              <ZoneBar
                                paint_pct={p.zone_distribution.paint_pct}
                                midrange_pct={p.zone_distribution.midrange_pct}
                                three_point_pct={p.zone_distribution.three_point_pct}
                                teamColor={teamColor(p.team)}
                              />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Card>
                </>
              )}
              {!analyticsQuery.isLoading && !analytics && job.status !== "complete" && (
                <Card className="mt-6 text-foreground/50">
                  Analytics will appear once processing is complete.
                </Card>
              )}
            </div>
          )}

          {/* ── Tab: Court Map ── */}
          {activeTab === "court" && (
            <div className="mt-6">
              {analyticsQuery.isLoading && (
                <Skeleton className="aspect-[94/50] w-full" />
              )}
              {analytics ? (
                <>
                  <CourtSVG players={analytics.players} telemetryAvailable={false} />
                  <FrameScrubber total={0} value={frame} onChange={setFrame} />
                </>
              ) : (
                !analyticsQuery.isLoading && (
                  <Card className="flex aspect-[94/50] max-h-[420px] items-center justify-center text-foreground/40">
                    Court map available after analysis completes
                  </Card>
                )
              )}
            </div>
          )}

          {/* ── Tab: Players ── */}
          {activeTab === "players" && (
            <div className="mt-6">
              {analyticsQuery.isLoading && (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-40" />)}
                </div>
              )}
              {analytics && (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {analytics.players.map((p: PlayerAnalytics) => (
                    <Card key={p.track_id}>
                      {/* Player header */}
                      <div className="mb-3 flex items-center gap-3">
                        <span
                          className="flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-black"
                          style={{ backgroundColor: trackColor(p.track_id) }}
                        >
                          #{p.track_id}
                        </span>
                        <div>
                          <span
                            className="rounded-full px-2 py-0.5 text-xs font-bold"
                            style={{ backgroundColor: `${teamColor(p.team)}20`, color: teamColor(p.team) }}
                          >
                            {p.team}
                          </span>
                        </div>
                      </div>

                      {/* Stats grid */}
                      <div className="mb-3 grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-xs text-foreground/50">Distance</p>
                          <p className="font-mono font-bold tabular-nums">{p.total_distance_m} m</p>
                        </div>
                        <div>
                          <p className="text-xs text-foreground/50">Avg speed</p>
                          <p className="font-mono font-bold tabular-nums">{p.avg_speed_ms} m/s</p>
                        </div>
                        <div>
                          <p className="text-xs text-foreground/50">Max speed</p>
                          <p className="font-mono font-bold tabular-nums">{p.max_speed_ms} m/s</p>
                        </div>
                        <div>
                          <p className="text-xs text-foreground/50">Coverage</p>
                          <p className="font-mono font-bold tabular-nums">{p.court_coverage_pct}%</p>
                        </div>
                      </div>

                      {/* Zone bar */}
                      <ZoneBar
                        paint_pct={p.zone_distribution.paint_pct}
                        midrange_pct={p.zone_distribution.midrange_pct}
                        three_point_pct={p.zone_distribution.three_point_pct}
                        teamColor={teamColor(p.team)}
                      />
                    </Card>
                  ))}
                </div>
              )}
              {!analyticsQuery.isLoading && !analytics && job.status !== "complete" && (
                <Card className="text-foreground/50">
                  Player cards will appear once analysis completes.
                </Card>
              )}
            </div>
          )}

          {/* ── Tab: Report ── */}
          {activeTab === "report" && (
            <div className="mt-6">
              <Card className="flex flex-col items-center gap-4 py-16 text-center text-foreground/40">
                <FileText size={40} strokeWidth={1.2} />
                <p className="text-lg font-medium">LLM coaching report will appear here after Phase 10.</p>
                <p className="max-w-sm text-sm">
                  An AI-generated coaching summary with tactical insights, player performance highlights,
                  and recommendations will be generated via the local Ollama model.
                </p>
              </Card>
            </div>
          )}
        </>
      )}
    </Shell>
  );
}
