/**
 * ZoneBar — horizontal distribution bar split into three basketball shot zones.
 * Width of each segment is proportional to the percentage.
 */
interface ZoneBarProps {
  paint_pct: number;
  midrange_pct: number;
  three_point_pct: number;
  teamColor?: string;
  className?: string;
}

export default function ZoneBar({
  paint_pct,
  midrange_pct,
  three_point_pct,
  teamColor = "#37d67a",
  className = "",
}: ZoneBarProps) {
  const total = paint_pct + midrange_pct + three_point_pct || 100;
  const segments = [
    { label: "Paint", pct: paint_pct, opacity: 1.0 },
    { label: "Mid", pct: midrange_pct, opacity: 0.65 },
    { label: "3PT", pct: three_point_pct, opacity: 0.4 },
  ];

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {/* Bar */}
      <div className="flex h-2.5 w-full overflow-hidden rounded-full">
        {segments.map(({ label, pct, opacity }) => (
          <div
            key={label}
            title={`${label}: ${pct.toFixed(0)}%`}
            style={{
              width: `${(pct / total) * 100}%`,
              backgroundColor: teamColor,
              opacity,
            }}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="flex gap-3 text-xs text-foreground/50">
        {segments.map(({ label, pct }) => (
          <span key={label}>
            <span
              className="mr-0.5 inline-block h-1.5 w-1.5 rounded-sm"
              style={{ backgroundColor: teamColor }}
            />
            {label} {pct.toFixed(0)}%
          </span>
        ))}
      </div>
    </div>
  );
}
