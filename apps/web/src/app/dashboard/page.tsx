"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "@/lib/api";
import { Card, Shell, StatusBadge } from "@/components/ui";

export default function DashboardPage() {
  const { data: jobs, isLoading, error } = useQuery({ queryKey: ["jobs"], queryFn: fetchJobs });
  return (
    <Shell>
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black">Dashboard</h1>
          <p className="mt-2 text-foreground/70">Uploaded videos and generated first-pass stats.</p>
        </div>
        <Link className="rounded-full bg-accent px-5 py-3 font-bold text-black" href="/upload">Upload</Link>
      </div>
      <div className="mt-6 grid gap-4">
        {isLoading && <Card>Loading jobs…</Card>}
        {error && <Card className="text-danger">Could not load jobs: {(error as Error).message}</Card>}
        {jobs?.length === 0 && <Card>No jobs yet. <Link className="text-accent" href="/upload">Upload your first clip.</Link></Card>}
        {jobs?.map((job) => (
          <Link key={job.job_id} href={`/dashboard/jobs/${job.job_id}`}>
            <Card className="flex flex-wrap items-center justify-between gap-4 hover:border-accent">
              <div>
                <div className="flex items-center gap-3"><h2 className="text-xl font-black">{job.label ?? job.original_filename}</h2><StatusBadge status={job.status} /></div>
                <p className="mt-1 text-sm text-foreground/60">{job.original_filename} · {(job.file_size_bytes / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <p className="font-mono text-2xl font-black">{job.progress_pct}%</p>
            </Card>
          </Link>
        ))}
      </div>
    </Shell>
  );
}
