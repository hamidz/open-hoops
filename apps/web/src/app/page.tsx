import Link from "next/link";
import { Activity, Upload, BarChart3, type LucideIcon } from "lucide-react";
import { Card, Shell } from "@/components/ui";

const steps: Array<[string, string, LucideIcon]> = [["1", "Select a fixed sideline video", Upload], ["2", "Open Hoops stores it locally", Activity], ["3", "Generated stats appear immediately", BarChart3]];

export default function Home() {
  return (
    <Shell>
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div>
          <p className="mb-3 text-sm font-bold uppercase tracking-[0.3em] text-accent">Local-first basketball analytics</p>
          <h1 className="text-5xl font-black leading-tight">Upload a clip. Get first-pass stats. Keep footage local.</h1>
          <p className="mt-5 max-w-2xl text-lg text-foreground/70">Open Hoops now includes a runnable first workflow: configure the stack, upload an MP4/MOV, and review generated player/team stats from your browser.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="rounded-full bg-accent px-5 py-3 font-bold text-black" href="/upload">Start first workflow</Link>
            <Link className="rounded-full border border-line px-5 py-3 font-bold" href="/dashboard">View dashboard</Link>
          </div>
        </div>
        <Card className="grid gap-4">
          {steps.map(([step, text, Icon]) => (
            <div key={String(step)} className="flex items-center gap-4 rounded-xl bg-panel-soft p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent font-mono font-black text-black">{String(step)}</div>
              <Icon className="h-5 w-5 text-accent-2" />
              <p className="font-semibold">{String(text)}</p>
            </div>
          ))}
        </Card>
      </section>
    </Shell>
  );
}
