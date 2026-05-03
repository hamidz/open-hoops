/**
 * Full NBA court SVG (94 × 50 ft coordinate space; 1 SVG unit = 1 ft).
 *
 * Props:
 *  - players: optional array of player positions in SVG court coordinates
 *  - telemetryAvailable: shows "no telemetry" overlay when false
 */
"use client";

import type { PlayerAnalytics } from "@/lib/types";

// ─── Court dimensions (feet) ──────────────────────────────────────────────────
const W = 94;
const H = 50;
const CX = W / 2;
const CY = H / 2;

// Basket positions (5.25 ft from endline, centred)
const BLX = 5.25; // left basket x
const BRX = W - 5.25; // right basket x

// Paint (19 ft deep from endline, 16 ft wide)
const PAINT_DEPTH = 19;
const PAINT_HALF_W = 8; // half of 16 ft

// Free-throw circle: 6 ft radius
const FT_R = 6;

// 3-point: 23.75 ft from basket; corner at 3 ft from sideline → 22 ft from basket
const THREE_R = 23.75;
const THREE_CORNER_Y = 3; // 3 ft from sideline
// x where corner line meets the arc
const THREE_CORNER_X_LEFT =
  BLX + Math.sqrt(THREE_R ** 2 - (CY - THREE_CORNER_Y) ** 2);
const THREE_CORNER_X_RIGHT =
  BRX - Math.sqrt(THREE_R ** 2 - (CY - THREE_CORNER_Y) ** 2);

// Center circle radius: 6 ft
const CENTER_R = 6;

// Restricted area: 4 ft from basket
const RESTRICTED_R = 4;

// ─── Track → colour mapping (design system) ───────────────────────────────────
const TRACK_COLORS: Record<number, string> = {
  1: "#60A5FA",
  2: "#F87171",
  3: "#34D399",
  4: "#FBBF24",
  5: "#A78BFA",
  6: "#FB923C",
  7: "#38BDF8",
  8: "#F472B6",
  9: "#A3E635",
  10: "#E879F9",
  11: "#94A3B8",
  12: "#FCD34D",
};

function trackColor(id: number): string {
  return TRACK_COLORS[id] ?? "#94A3B8";
}

// ─── Static position derivation from zone distribution ────────────────────────
// Used when we have analytics but not per-frame telemetry.
function mockCourtPosition(
  player: PlayerAnalytics,
): { x: number; y: number } {
  const { paint_pct, midrange_pct, three_point_pct } = player.zone_distribution;
  const isHome = player.team === "home";
  const seed = player.track_id;

  // Pick dominant zone
  const dominant =
    paint_pct >= midrange_pct && paint_pct >= three_point_pct
      ? "paint"
      : three_point_pct >= midrange_pct
        ? "three"
        : "mid";

  // Deterministic scatter within zone based on track_id
  const scatter = ((seed * 7) % 5) - 2; // −2 … +2

  if (dominant === "paint") {
    return isHome
      ? { x: BLX + 8 + scatter, y: CY + (seed % 3 === 0 ? -5 : seed % 3 === 1 ? 5 : 0) }
      : { x: BRX - 8 - scatter, y: CY + (seed % 3 === 0 ? -5 : seed % 3 === 1 ? 5 : 0) };
  }
  if (dominant === "three") {
    const angle = isHome
      ? (Math.PI / 5) * (seed % 5) - Math.PI / 2.5
      : Math.PI - (Math.PI / 5) * (seed % 5) + Math.PI / 2.5;
    return {
      x: (isHome ? BLX : BRX) + Math.cos(angle) * (THREE_R - 1),
      y: CY + Math.sin(angle) * (THREE_R - 1),
    };
  }
  // mid-range
  return isHome
    ? { x: BLX + PAINT_DEPTH + 4 + scatter, y: CY + (seed % 2 === 0 ? -9 : 9) }
    : { x: BRX - PAINT_DEPTH - 4 - scatter, y: CY + (seed % 2 === 0 ? -9 : 9) };
}

// ─── SVG court drawing helpers ────────────────────────────────────────────────

/** Left 3-point arc: SVG path from (THREE_CORNER_X_LEFT, THREE_CORNER_Y) around
 *  the left basket to (THREE_CORNER_X_LEFT, H − THREE_CORNER_Y). */
function leftArcPath(): string {
  const x1 = THREE_CORNER_X_LEFT;
  const y1 = THREE_CORNER_Y;
  const y2 = H - THREE_CORNER_Y;
  return `M ${x1} ${y1} A ${THREE_R} ${THREE_R} 0 0 0 ${x1} ${y2}`;
}

function rightArcPath(): string {
  const x1 = THREE_CORNER_X_RIGHT;
  const y1 = THREE_CORNER_Y;
  const y2 = H - THREE_CORNER_Y;
  return `M ${x1} ${y1} A ${THREE_R} ${THREE_R} 0 0 1 ${x1} ${y2}`;
}

// ─── Component ────────────────────────────────────────────────────────────────

interface CourtPlayerPos {
  track_id: number;
  x: number; // court feet
  y: number; // court feet
  label?: string;
  color?: string;
}

interface CourtSVGProps {
  /** Analytics players used to derive static mock positions */
  players?: PlayerAnalytics[];
  /** Override with explicit positions (e.g. from telemetry frame) */
  positions?: CourtPlayerPos[];
  telemetryAvailable?: boolean;
  className?: string;
}

export default function CourtSVG({
  players,
  positions,
  telemetryAvailable = false,
  className = "",
}: CourtSVGProps) {
  const LINE = "#355545";
  const SURFACE = "#0f1d17";
  const PAINT_FILL = "rgba(21,40,26,0.7)";
  const LINE_W = 0.35;
  const LINE_W_HEAVY = 0.5;

  // Resolve player dots
  const dots: CourtPlayerPos[] =
    positions ??
    (players ?? []).map((p) => {
      const pos = mockCourtPosition(p);
      return { track_id: p.track_id, x: pos.x, y: pos.y, color: trackColor(p.track_id) };
    });

  return (
    <div className={`relative ${className}`}>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full rounded-xl"
        style={{ background: SURFACE }}
        aria-label="Basketball court diagram"
      >
        {/* ── Court boundary ── */}
        <rect
          x={0} y={0} width={W} height={H}
          fill="none" stroke={LINE} strokeWidth={LINE_W_HEAVY}
        />

        {/* ── Center line ── */}
        <line x1={CX} y1={0} x2={CX} y2={H} stroke={LINE} strokeWidth={LINE_W} />

        {/* ── Center circle ── */}
        <circle cx={CX} cy={CY} r={CENTER_R} fill="none" stroke={LINE} strokeWidth={LINE_W} />

        {/* ── Left paint ── */}
        <rect
          x={0} y={CY - PAINT_HALF_W} width={PAINT_DEPTH} height={PAINT_HALF_W * 2}
          fill={PAINT_FILL} stroke={LINE} strokeWidth={LINE_W}
        />

        {/* ── Right paint ── */}
        <rect
          x={W - PAINT_DEPTH} y={CY - PAINT_HALF_W} width={PAINT_DEPTH} height={PAINT_HALF_W * 2}
          fill={PAINT_FILL} stroke={LINE} strokeWidth={LINE_W}
        />

        {/* ── Left free-throw circle (top half dashed) ── */}
        <path
          d={`M ${BLX + PAINT_DEPTH} ${CY - FT_R} A ${FT_R} ${FT_R} 0 0 1 ${BLX + PAINT_DEPTH} ${CY + FT_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W}
        />
        <path
          d={`M ${BLX + PAINT_DEPTH} ${CY - FT_R} A ${FT_R} ${FT_R} 0 0 0 ${BLX + PAINT_DEPTH} ${CY + FT_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W} strokeDasharray="1 1"
        />

        {/* ── Right free-throw circle ── */}
        <path
          d={`M ${BRX - PAINT_DEPTH} ${CY - FT_R} A ${FT_R} ${FT_R} 0 0 0 ${BRX - PAINT_DEPTH} ${CY + FT_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W}
        />
        <path
          d={`M ${BRX - PAINT_DEPTH} ${CY - FT_R} A ${FT_R} ${FT_R} 0 0 1 ${BRX - PAINT_DEPTH} ${CY + FT_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W} strokeDasharray="1 1"
        />

        {/* ── Left restricted area ── */}
        <path
          d={`M ${BLX} ${CY - RESTRICTED_R} A ${RESTRICTED_R} ${RESTRICTED_R} 0 0 1 ${BLX} ${CY + RESTRICTED_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W}
        />

        {/* ── Right restricted area ── */}
        <path
          d={`M ${BRX} ${CY - RESTRICTED_R} A ${RESTRICTED_R} ${RESTRICTED_R} 0 0 0 ${BRX} ${CY + RESTRICTED_R}`}
          fill="none" stroke={LINE} strokeWidth={LINE_W}
        />

        {/* ── Left 3-point line ── */}
        <line x1={0} y1={THREE_CORNER_Y} x2={THREE_CORNER_X_LEFT} y2={THREE_CORNER_Y}
          stroke={LINE} strokeWidth={LINE_W_HEAVY} />
        <line x1={0} y1={H - THREE_CORNER_Y} x2={THREE_CORNER_X_LEFT} y2={H - THREE_CORNER_Y}
          stroke={LINE} strokeWidth={LINE_W_HEAVY} />
        <path d={leftArcPath()} fill="none" stroke={LINE} strokeWidth={LINE_W_HEAVY} />

        {/* ── Right 3-point line ── */}
        <line x1={W} y1={THREE_CORNER_Y} x2={THREE_CORNER_X_RIGHT} y2={THREE_CORNER_Y}
          stroke={LINE} strokeWidth={LINE_W_HEAVY} />
        <line x1={W} y1={H - THREE_CORNER_Y} x2={THREE_CORNER_X_RIGHT} y2={H - THREE_CORNER_Y}
          stroke={LINE} strokeWidth={LINE_W_HEAVY} />
        <path d={rightArcPath()} fill="none" stroke={LINE} strokeWidth={LINE_W_HEAVY} />

        {/* ── Baskets ── */}
        <circle cx={BLX} cy={CY} r={0.75} fill="none" stroke="#F97316" strokeWidth={0.4} />
        <circle cx={BRX} cy={CY} r={0.75} fill="none" stroke="#F97316" strokeWidth={0.4} />

        {/* ── Player markers ── */}
        {dots.map((d) => (
          <g key={d.track_id} transform={`translate(${d.x},${d.y})`}>
            <circle r={1.2} fill={d.color ?? trackColor(d.track_id)} stroke="white" strokeWidth={0.25} />
            <text
              x={0} y={0.45}
              textAnchor="middle"
              fontSize={0.95}
              fontWeight="bold"
              fill="white"
            >
              {d.label ?? d.track_id}
            </text>
          </g>
        ))}
      </svg>

      {!telemetryAvailable && (
        <div className="pointer-events-none absolute inset-0 flex items-end justify-center rounded-xl pb-4">
          <span className="rounded-full bg-panel/80 px-3 py-1 text-xs text-foreground/50 backdrop-blur">
            Static positions — telemetry available after CV processing
          </span>
        </div>
      )}
    </div>
  );
}
