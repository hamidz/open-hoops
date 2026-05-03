from datetime import datetime, timezone
from random import Random

from app.models import AnalyticsSummary, PlayerAnalytics, ZoneDistribution


def generate_first_workflow_stats(job_id: str, file_size_bytes: int) -> AnalyticsSummary:
    """Return deterministic MVP stats until later phases replace this with CV analytics."""
    rng = Random(job_id)
    size_factor = max(1, min(12, file_size_bytes // 1_000_000 + 1))
    players: list[PlayerAnalytics] = []
    for track_id in range(1, 11):
        team = "home" if track_id <= 5 else "away"
        distance = round(rng.uniform(210, 420) * size_factor / 3, 1)
        avg_speed = round(rng.uniform(1.8, 4.6), 2)
        paint = round(rng.uniform(18, 38), 1)
        mid = round(rng.uniform(28, 48), 1)
        three = round(max(0.0, 100 - paint - mid), 1)
        players.append(
            PlayerAnalytics(
                track_id=track_id,
                label=f"Player {track_id}",
                team=team,
                total_distance_m=distance,
                avg_speed_ms=avg_speed,
                max_speed_ms=round(avg_speed + rng.uniform(2.0, 4.5), 2),
                court_coverage_pct=round(rng.uniform(24, 56), 1),
                zone_distribution=ZoneDistribution(
                    paint_pct=paint,
                    midrange_pct=mid,
                    three_point_pct=three,
                ),
            )
        )
    return AnalyticsSummary(
        job_id=job_id,
        computed_at=datetime.now(timezone.utc),
        duration_seconds=300,
        total_sampled_frames=900,
        avg_detections_per_frame=9.4,
        ball_tracking_coverage_pct=72.5,
        team_spacing_avg_m=round(rng.uniform(4.5, 7.5), 2),
        players=players,
    )
