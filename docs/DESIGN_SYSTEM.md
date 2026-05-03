# Design System — Open Hoops

> Visual design specification for the Open Hoops analytics platform.
> All frontend implementation must follow this document. Update it before changing visual decisions.

---

## 1. Design Philosophy

Open Hoops is a **data-dense, coach-focused analytics tool** used in dim gym environments and on bright office monitors. The visual language must:

- Prioritize data legibility over decorative design.
- Use dark mode as the primary experience (court visualizations are dramatically more legible on dark backgrounds).
- Communicate confidence and uncertainty — tracking data is imperfect and the UI must reflect that.
- Be consistent enough that coaches can focus on content, not learn new UI patterns per page.

---

## 2. Color System

### 2.1 Brand Palette

```
Primary:   --color-brand-500  #F97316  (energetic orange — basketball, action)
           --color-brand-400  #FB923C
           --color-brand-600  #EA580C

Neutral:   --color-court-900  #0F1117  (near-black — primary dark background)
           --color-court-800  #1A1D27  (dark card/panel background)
           --color-court-700  #252836  (raised surface, hover states)
           --color-court-600  #343848  (borders, dividers)
           --color-court-400  #6B7280  (muted text, labels)
           --color-court-200  #C8CBD4  (secondary text)
           --color-court-100  #E8E9EC  (primary text on dark)
           --color-court-50   #F5F6F8  (inverse background for light contexts)
```

### 2.2 Semantic Color Tokens

These tokens map brand/neutral colors to intent. Always use semantic tokens in components, never raw hex values:

```
--color-bg-base         : court-900    (page background)
--color-bg-surface      : court-800    (card, panel, modal)
--color-bg-raised       : court-700    (hover state, active element)
--color-border          : court-600    (all borders)
--color-text-primary    : court-100    (headings, important content)
--color-text-secondary  : court-200    (body text)
--color-text-muted      : court-400    (labels, captions, placeholders)
--color-text-inverse    : court-900    (text on light/brand backgrounds)

--color-accent          : brand-500    (CTAs, active states, links)
--color-accent-hover    : brand-400    (hover on accent elements)

--color-success         : #22C55E      (green-500 — calibration good, job complete)
--color-warning         : #EAB308      (yellow-500 — calibration review needed)
--color-error           : #EF4444      (red-500 — calibration poor, job failed)
--color-info            : #3B82F6      (blue-500 — informational states)

--color-processing      : brand-500    (animated, job in progress)
```

### 2.3 Data Encoding Colors

#### Team Colors (user-assignable defaults)

```
Home team default:   #1D4ED8  (blue-700)
Away team default:   #DC2626  (red-600)
```

Users can override team colors in the annotation panel. These defaults must have sufficient contrast against the court surface color.

#### Player Track Colors (10-track palette)

When players are not yet assigned to teams, assign colors by track_id order. This palette is designed for maximum differentiation on dark backgrounds:

```
Track 1:   #60A5FA   (blue-400)
Track 2:   #F87171   (red-400)
Track 3:   #34D399   (emerald-400)
Track 4:   #FBBF24   (amber-400)
Track 5:   #A78BFA   (violet-400)
Track 6:   #FB923C   (orange-400)
Track 7:   #38BDF8   (sky-400)
Track 8:   #F472B6   (pink-400)
Track 9:   #A3E635   (lime-400)
Track 10:  #E879F9   (fuchsia-400)
Track 11:  #94A3B8   (slate-400, ball track)
Track 12:  #FCD34D   (yellow-300)
```

#### Heatmap Color Scale

Use **Inferno** as the primary heatmap color scale for player density:

```
Low density:    #000004  (near black)
Medium-low:     #56106E
Medium:         #BB3754
Medium-high:    #F98C0A
High density:   #FCFFA4  (near white/yellow)
```

Inferno is perceptually uniform, colorblind-safe, and works well on dark backgrounds. Available as a D3 scale: `d3.scaleSequential(d3.interpolateInferno)`.

For **team heatmaps**, tint the Inferno scale toward the team's assigned color using `d3.interpolateRgb`.

---

## 3. Typography

### 3.1 Font Selection

```
Display / Headings:  "Inter Variable"  (Google Fonts, variable font — weight 400–800)
Body / UI:           "Inter Variable"  (same family, weight 400–500)
Data / Stats:        "JetBrains Mono"  (tabular numerics, monospace for stats columns)
```

> **Why Inter:** Neutral, highly legible at small sizes, variable weight allows tight control without multiple font files.
> **Why JetBrains Mono for stats:** Stats columns (distance, speed, coverage %) must column-align. Proportional fonts cause numbers to jitter in sorted tables. Monospace solves this.

### 3.2 Type Scale

```
--text-xs     : 0.75rem  / 12px  — chart axis labels, captions
--text-sm     : 0.875rem / 14px  — body text, table cells, form labels
--text-base   : 1rem     / 16px  — default body
--text-lg     : 1.125rem / 18px  — card titles, section headers
--text-xl     : 1.25rem  / 20px  — page section headings
--text-2xl    : 1.5rem   / 24px  — page titles
--text-3xl    : 1.875rem / 30px  — dashboard hero stats

Line height:   1.5  for body, 1.25 for headings, 1.0 for stat numbers
```

### 3.3 Font Weight Usage

```
400 — body text, table cells
500 — UI labels, navigation items
600 — card titles, active states
700 — page headings, stat numbers
800 — hero stats, key metrics
```

### 3.4 Tailwind Font Config

Add to `tailwind.config.ts`:

```ts
fontFamily: {
  sans: ['Inter Variable', 'Inter', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
},
```

---

## 4. Component Library

### 4.1 shadcn/ui (Primary Component System)

All UI components use **shadcn/ui** (Radix UI + Tailwind) as the base primitive layer. Components are added via:

```bash
npx shadcn-ui@latest add button card badge dialog sheet tabs select toast
```

Generated components live in `apps/web/src/components/ui/`. Never modify auto-generated files without adding a comment explaining the deviation from the shadcn default.

**Components required for MVP:**

| Component | Usage |
|---|---|
| `Button` | All actions |
| `Card` | Job cards, stat cards, player cards |
| `Badge` | Job status indicators |
| `Dialog` | Confirmation modals |
| `Sheet` | Mobile-friendly side panels |
| `Tabs` | Dashboard tab navigation |
| `Select` | Court type, player, team selectors |
| `Progress` | Job progress bar |
| `Toast` (Sonner) | Upload success, error, job state changes |
| `Skeleton` | Loading states for all async content |
| `Slider` | Heatmap opacity, frame scrubber |
| `Table` | Player stats table |
| `Tooltip` | Stat card explanations |
| `ScrollArea` | Job list, long player lists |

### 4.2 Icon System — Lucide React

```bash
npm install lucide-react
```

Standard icon usage:
- Status icons: `CheckCircle`, `XCircle`, `Clock`, `Loader2` (animated)
- Navigation: `LayoutDashboard`, `Upload`, `Settings`, `ChevronRight`
- Actions: `Trash2`, `RefreshCw`, `Download`, `Copy`, `Play`, `Pause`
- Court: `Map`, `Target`, `Zap`
- Player: `User`, `Users`, `Tag`

All icons use `size={16}` for inline/button, `size={20}` for standalone, `size={24}` for section headers. Never use icon-only buttons without an accessible label.

### 4.3 Custom Components

These components do not exist in shadcn/ui and must be built for this project:

| Component | Location | Purpose |
|---|---|---|
| `CourtSVG` | `components/court/CourtSVG.tsx` | Scalable court diagram with player overlays |
| `HeatmapOverlay` | `components/court/HeatmapOverlay.tsx` | D3 KDE heatmap rendered over CourtSVG |
| `PlayerTrail` | `components/court/PlayerTrail.tsx` | Animated movement trail on CourtSVG |
| `FrameScrubber` | `components/court/FrameScrubber.tsx` | Timeline slider with frame preview |
| `CalibrationCanvas` | `components/calibration/CalibrationCanvas.tsx` | Interactive calibration point placement |
| `CourtReferencePanel` | `components/calibration/CourtReferencePanel.tsx` | Reference court with named calibration points |
| `StatCard` | `components/analytics/StatCard.tsx` | Metric card with value, label, delta, confidence |
| `ZoneBar` | `components/analytics/ZoneBar.tsx` | Zone distribution bar (paint / mid / 3pt) |
| `JobStatusBadge` | `components/jobs/JobStatusBadge.tsx` | Animated status badge with icon |
| `TrackingCoverageWarning` | `components/jobs/TrackingCoverageWarning.tsx` | Low coverage callout |

---

## 5. Court SVG Visual Language

The court SVG is the primary visual output. Every visual property must be specified.

### 5.1 Court Surface and Lines

```
Court surface fill:    #1A1D27  (--color-bg-surface — dark hardwood suggestion)
Court boundary:        #343848  (--color-border — subtle outer edge)
Court line color:      #4B5563  (gray-600 — legible but not competing with data)
Court line width:      1.5px for standard lines
Court line width:      2px for 3pt arc, center circle, paint boundary
Paint area fill:       rgba(52, 56, 72, 0.5)  (subtle fill, same family as surface)
Center circle fill:    none
```

### 5.2 Player Markers

```
Shape:          Circle
Size:           8px radius when court is full-width (1200px)
                Scales proportionally with court SVG size
Fill:           Team color (or track color if unassigned)
Stroke:         2px white for visibility
Label:          Player number inside circle (white, 10px, bold)
Ball marker:    8px orange circle (#F97316) with dashed stroke
```

### 5.3 Player Trails

```
Stroke:         Team color at 40% opacity
Stroke width:   2px
Dash:           none (solid)
Fade:           Gradient from current frame (40% opacity) to oldest frame (0%)
Length:         Show last 60 frames by default (2 seconds at 30fps)
```

### 5.4 Calibration Point Markers

```
Active (placing):  12px yellow circle (#FBBF24) with pulsing ring animation
Placed:            10px circle with team-like color, number label
Hover:             scale(1.2) transform
Cursor:            crosshair when over frame image
```

### 5.5 Shot Markers

```
Made shot:      Solid circle, team color, 8px
Missed shot:    X mark, gray (#6B7280), 8px
3pt zone:       Outline only (no fill)
2pt zone:       No additional marking
```

### 5.6 CourtSVG Props

```tsx
interface CourtSVGProps {
  orientation: 'full' | 'half-left' | 'half-right'
  courtType: 'nba' | 'fiba'
  width?: number          // SVG viewport width in px
  players?: PlayerPosition[]
  showTrails?: boolean
  trailLength?: number    // frames
  showShots?: boolean
  shots?: ShotAnnotation[]
  showHeatmap?: boolean
  heatmapLayer?: HeatmapGrid
  activeFrameIndex?: number
  selectedPlayerId?: number | null
  onCourtClick?: (courtXY: [number, number]) => void
}
```

---

## 6. Spacing and Layout

### 6.1 Spacing Scale

Use Tailwind's default spacing scale. Key breakpoints for this project:

```
p-2   / 8px   — icon padding, compact items
p-3   / 12px  — button padding
p-4   / 16px  — card padding (default)
p-6   / 24px  — section padding
p-8   / 32px  — page padding
gap-4 / 16px  — grid gaps
```

### 6.2 Layout Grid

```
Sidebar width:    240px (fixed, collapsible to 64px icon mode)
Main content:     flex-1, max-w-7xl, centered
Tab content:      full width within main
Dashboard grid:   12-column CSS grid
Stat cards:       span 3 columns (4 per row on desktop)
Court view:       span 8 columns
Player list:      span 4 columns
```

### 6.3 Responsive Strategy

The MVP targets 1280px+ wide desktop/laptop screens. However, the layout must not break at:

```
1024px:  Sidebar collapses to icon mode; main content full width
768px:   Single column, sidebar hides behind hamburger menu
< 768px: Not required to be functional; add a "use on desktop" banner
```

Use Tailwind responsive prefixes: `md:`, `lg:`, `xl:` for breakpoints.

---

## 7. Motion and Animation

### 7.1 Transition Tokens

```
--duration-fast    : 100ms  — hover states, immediate feedback
--duration-default : 200ms  — button press, toggle, expand
--duration-slow    : 400ms  — panel open/close, skeleton → content
--duration-spin    : 1000ms — loading spinner (linear repeat)
```

Use `transition-all duration-200 ease-out` as the Tailwind default.

### 7.2 Loading States

Every async data fetch must show a `Skeleton` component before content loads:

| Context | Skeleton Type |
|---|---|
| Job list | `Skeleton` rows, 3–5 lines, simulating job cards |
| Court SVG | `Skeleton` rectangle matching court aspect ratio |
| Heatmap overlay | Fade-in after computation (no skeleton — show empty court first) |
| Player stats cards | `Skeleton` cards in a 4-column grid |
| Calibration frame | `Skeleton` full-width rectangle with aspect-ratio preserved |
| Analytics summary | `Skeleton` stat cards (4 per row) |

Never show a blank white or black void while content loads.

### 7.3 Job Status Animations

| Status | Visual Treatment |
|---|---|
| `queued` | Static badge, clock icon |
| `processing` | `Loader2` icon with `animate-spin`, progress bar `animate-pulse` |
| `calibration_needed` | Warning badge, pulsing orange dot |
| `complete` | `CheckCircle` icon, badge transition with `animate-in fade-in` |
| `failed` | `XCircle` icon, error badge, no animation |

### 7.4 Calibration Interactions

```
New point placement:  scale 0 → 1 spring animation (150ms)
Point drag:           Direct cursor tracking, no spring (zero latency)
Compute button enable: Subtle green pulse to draw attention
Reprojection overlay: Fade in (300ms) after computation
```

---

## 8. Dark Mode

Dark mode is the **default and primary** mode. Light mode is not required for MVP.

All color tokens are defined for dark mode. If light mode is added later, tokens will be inverted via `@media (prefers-color-scheme: light)`.

Tailwind config:
```ts
darkMode: 'class',  // class-based, not media-query — allows future toggle
```

The `<html>` element always has class `dark` for MVP.

---

## 9. Accessibility Baseline

- **Contrast:** All text meets WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text). All semantic tokens are defined with contrast in mind.
- **Focus indicators:** `ring-2 ring-brand-500 ring-offset-2 ring-offset-court-900` applied to all interactive elements on keyboard focus.
- **Color independence:** Every status (job status, calibration quality, tracking coverage) is communicated with both color AND text/icon. Never color-only.
- **Motion:** No animations that loop continuously or flash unless paused with `prefers-reduced-motion`. Use `motion-safe:` Tailwind variant.
- **Font sizes:** Minimum 12px for any visible text (no sub-10px micro labels in charts).

---

## 10. Tailwind Config Extension

The following additions are required in `apps/web/tailwind.config.ts`:

```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
        },
        court: {
          50:  '#F5F6F8',
          100: '#E8E9EC',
          200: '#C8CBD4',
          400: '#6B7280',
          600: '#343848',
          700: '#252836',
          800: '#1A1D27',
          900: '#0F1117',
        },
      },
      fontFamily: {
        sans: ['Inter Variable', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // tabular stats — used with font-mono
        'stat-sm': ['0.875rem', { lineHeight: '1', fontVariantNumeric: 'tabular-nums' }],
        'stat-lg': ['1.5rem',   { lineHeight: '1', fontVariantNumeric: 'tabular-nums' }],
        'stat-xl': ['1.875rem', { lineHeight: '1', fontVariantNumeric: 'tabular-nums' }],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 200ms ease-out',
        'scale-in': 'scaleIn 150ms ease-out',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        scaleIn: { '0%': { transform: 'scale(0)' }, '100%': { transform: 'scale(1)' } },
      },
    },
  },
  plugins: [],
}

export default config
```

---

## 11. Design Review Gates

- **Phase 03:** Owner validates dark-mode dashboard with mock data, stat cards, and court SVG visual appearance.
- **Phase 06:** Owner validates calibration canvas interaction, point marker styles, and reprojection overlay appearance.
- **Phase 08:** Owner validates heatmap color scale (Inferno), opacity slider, and court overlay legibility.
- **Phase 11:** Owner validates annotation panel layout and player card visual treatment.
