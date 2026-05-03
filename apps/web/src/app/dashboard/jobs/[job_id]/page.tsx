"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteJob, fetchAnalytics, fetchJob } from "@/lib/api";
import { Card, Shell, Stat, StatusBadge } from "@/components/ui";

export default function JobDetailPage() {
  const params = useParams<{ job_id: string }>();
  const jobId = params.job_id;
  const router = useRouter();
  const queryClient = useQueryClient();
  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "complete" || status === "failed" ? false : 3000;
    },
  });
  const analyticsQuery = useQuery({ queryKey: ["analytics", jobId], queryFn: () => fetchAnalytics(jobId), enabled: jobQuery.data?.status === "complete" });
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
      {jobQuery.isLoading && <Card className="mt-6">Loading job…</Card>}
      {jobQuery.error && <Card className="mt-6 text-danger">Could not load job: {(jobQuery.error as Error).message}</Card>}
      {job && (
        <>
          <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3"><h1 className="text-4xl font-black">{job.label ?? job.original_filename}</h1><StatusBadge status={job.status} /></div>
              <p className="mt-2 text-foreground/70">{job.original_filename} · {(job.file_size_bytes / 1024 / 1024).toFixed(2)} MB · uploaded {new Date(job.created_at).toLocaleString()}</p>
            </div>
            {job.status !== "processing" && (
              <button
                className="rounded-full border border-danger px-4 py-2 font-bold text-danger disabled:opacity-50"
                disabled={deleteMutation.isPending}
                onClick={() => { if (confirm("Delete this job?")) deleteMutation.mutate(); }}
              >
                {deleteMutation.isPending ? "Deleting…" : "Delete"}
              </button>
            )}
          </div>
          <div className="mt-6 h-3 overflow-hidden rounded-full bg-panel"><div className="h-full bg-accent" style={{ width: `${job.progress_pct}%` }} /></div>
          {job.status === "calibration_needed" && <Card className="mt-6"><Link className="text-accent" href={`/dashboard/jobs/${job.job_id}/calibrate`}>Calibrate Now</Link></Card>}
          {job.status === "failed" && <Card className="mt-6 text-danger">{job.error_message ?? "Job failed."}</Card>}
          {deleteMutation.error && <Card className="mt-6 text-danger">Delete failed: {(deleteMutation.error as Error).message}</Card>}
          {analyticsQuery.isLoading && <Card className="mt-6">Loading analytics…</Card>}
          {analytics && (
            <>
              <div className="mt-6 grid gap-4 md:grid-cols-4">
                <Stat label="Players" value={analytics.players.length} />
                <Stat label="Duration" value={`${Math.round(analytics.duration_seconds / 60)} min`} />
                <Stat label="Team spacing" value={`${analytics.team_spacing_avg_m} m`} />
                <Stat label="Ball coverage" value={`${analytics.ball_tracking_coverage_pct}%`} />
              </div>
              <Card className="mt-6 overflow-x-auto">
                <h2 className="mb-4 text-2xl font-black">Player stats</h2>
                <table className="w-full min-w-[720px] text-left text-sm">
                  <thead className="text-foreground/60"><tr><th className="py-2">Track</th><th>Team</th><th>Distance</th><th>Avg speed</th><th>Max speed</th><th>Coverage</th><th>Zones</th></tr></thead>
                  <tbody>
                    {analytics.players.map((player) => (
                      <tr key={player.track_id} className="border-t border-line/60">
                        <td className="py-3 font-mono">#{player.track_id}</td><td>{player.team}</td><td className="font-mono">{player.total_distance_m} m</td><td className="font-mono">{player.avg_speed_ms} m/s</td><td className="font-mono">{player.max_speed_ms} m/s</td><td className="font-mono">{player.court_coverage_pct}%</td>
                        <td><div className="flex h-2 overflow-hidden rounded-full bg-panel-soft"><span className="bg-accent" style={{ width: `${player.zone_distribution.paint_pct}%` }} /><span className="bg-accent-2" style={{ width: `${player.zone_distribution.midrange_pct}%` }} /><span className="bg-white/60" style={{ width: `${player.zone_distribution.three_point_pct}%` }} /></div></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </>
          )}
        </>
      )}
    </Shell>
  );
}
