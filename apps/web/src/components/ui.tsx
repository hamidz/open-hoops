import Link from "next/link";
import type { ReactNode } from "react";

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-line/70 bg-panel/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-xl font-black tracking-tight">Open Hoops</Link>
          <nav className="flex gap-3 text-sm text-foreground/80">
            <Link className="rounded-full px-3 py-2 hover:bg-panel-soft" href="/upload">Upload</Link>
            <Link className="rounded-full px-3 py-2 hover:bg-panel-soft" href="/dashboard">Dashboard</Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-line/80 bg-panel/90 p-5 shadow-xl shadow-black/10 ${className}`}>{children}</section>;
}

export function StatusBadge({ status }: { status: string }) {
  const color = status === "complete" ? "bg-accent/15 text-accent" : status === "failed" ? "bg-danger/15 text-danger" : "bg-accent-2/15 text-accent-2";
  return <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide ${color}`}>{status.replace("_", " ")}</span>;
}

export function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <p className="text-sm text-foreground/60">{label}</p>
      <p className="mt-2 font-mono text-3xl font-black tabular-nums">{value}</p>
    </Card>
  );
}
