"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Pause, Play, SkipBack, SkipForward } from "lucide-react";

interface FrameScrubberProps {
  /** Total number of frames in the telemetry stream. 0 = no telemetry. */
  total: number;
  value: number;
  onChange: (frame: number) => void;
  fps?: number;
}

export default function FrameScrubber({
  total,
  value,
  onChange,
  fps = 30,
}: FrameScrubberProps) {
  const [playing, setPlaying] = useState(false);
  const rafRef = useRef<ReturnType<typeof requestAnimationFrame> | null>(null);
  const lastTsRef = useRef<number | null>(null);

  // ── Playback loop ─────────────────────────────────────────────────────────
  const tick = useCallback(
    (ts: number) => {
      if (lastTsRef.current === null) {
        lastTsRef.current = ts;
      }
      const elapsed = ts - lastTsRef.current;
      const frameDuration = 1000 / fps;
      if (elapsed >= frameDuration) {
        lastTsRef.current = ts;
        onChange((prev: number) => {
          const next = prev + 1;
          if (next >= total) {
            setPlaying(false);
            return prev;
          }
          return next;
        });
      }
      rafRef.current = requestAnimationFrame(tick);
    },
    [fps, onChange, total],
  );

  useEffect(() => {
    if (playing && total > 0) {
      rafRef.current = requestAnimationFrame(tick);
    } else {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      lastTsRef.current = null;
    }
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [playing, tick, total]);

  // ── Keyboard bindings ─────────────────────────────────────────────────────
  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      if (total === 0) return;
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        onChange(Math.max(0, value - 1));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        onChange(Math.min(total - 1, value + 1));
      } else if (e.key === " ") {
        e.preventDefault();
        setPlaying((p) => !p);
      }
    },
    [total, value, onChange],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  const disabled = total === 0;

  return (
    <div className="mt-3 flex flex-col gap-2 rounded-xl bg-panel px-4 py-3">
      {/* Controls row */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          aria-label="First frame"
          disabled={disabled}
          onClick={() => onChange(0)}
          className="rounded p-1 text-foreground/60 hover:text-foreground disabled:opacity-30"
        >
          <SkipBack size={16} />
        </button>

        <button
          type="button"
          aria-label={playing ? "Pause" : "Play"}
          disabled={disabled}
          onClick={() => setPlaying((p) => !p)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-accent hover:bg-accent/30 disabled:opacity-30"
        >
          {playing ? <Pause size={16} /> : <Play size={16} />}
        </button>

        <button
          type="button"
          aria-label="Last frame"
          disabled={disabled}
          onClick={() => onChange(Math.max(0, total - 1))}
          className="rounded p-1 text-foreground/60 hover:text-foreground disabled:opacity-30"
        >
          <SkipForward size={16} />
        </button>

        <span className="ml-auto font-mono text-xs text-foreground/50">
          {disabled ? "No telemetry" : `${value + 1} / ${total}`}
        </span>
      </div>

      {/* Slider */}
      <input
        type="range"
        min={0}
        max={Math.max(0, total - 1)}
        value={disabled ? 0 : value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line accent-accent disabled:opacity-30"
        aria-label="Frame position"
      />

      <p className="text-xs text-foreground/40">
        ← → step frame · Space play/pause
      </p>
    </div>
  );
}
