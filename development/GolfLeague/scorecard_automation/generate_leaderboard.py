#!/usr/bin/env python3
"""
Generate season standings leaderboard HTML from golf league data.
Reads matches + scores + teams data and produces a print-ready standings page.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths — resolve relative to this script's location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path("/home/thecarter34/.openclaw/workspace/development/GolfLeague/golf_league_app/data")
OUTPUT_DIR = SCRIPT_DIR / "output"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_position(rank: int, ties: set[int]) -> str:
    """Return '1', '2', 'T8', etc."""
    if rank in ties:
        return f"T{rank}"
    return str(rank)


def generate_leaderboard(
    matches_path: Path = DATA_DIR / "matches.json",
    scores_path: Path = DATA_DIR / "scores.json",
    teams_path: Path = DATA_DIR / "teams.json",
    output_path: Path = OUTPUT_DIR / "leaderboard.html",
) -> str:
    matches = load_json(matches_path)
    scores = load_json(scores_path)
    teams = load_json(teams_path)

    # Accumulate points per team
    team_points: dict[str, float] = defaultdict(float)
    team_names: dict[str, str] = {}

    for team_id, team_data in teams.items():
        team_names[team_id] = team_data["name"]
        team_points[team_id] = 0.0

    # Collect all week numbers for the subtitle
    week_numbers = set()

    for match_id, match_data in matches.items():
        if not match_data.get("completed"):
            continue

        week_number = match_data.get("week_number")
        if week_number is not None:
            week_numbers.add(week_number)

        score_data = scores.get(match_id)
        if not score_data:
            continue

        team1_id = match_data["team1_id"]
        team2_id = match_data["team2_id"]
        team1_pts = score_data.get("team1_final_points", 0)
        team2_pts = score_data.get("team2_final_points", 0)

        team_points[team1_id] += team1_pts
        team_points[team2_id] += team2_pts

    # Build sorted standings
    standings = sorted(team_points.items(), key=lambda x: -x[1])

    # Assign positions with tie handling
    ranked = []
    seen_scores: dict[float, int] = {}
    pos = 1
    for i, (team_id, pts) in enumerate(standings):
        if pts not in seen_scores:
            seen_scores[pts] = pos
        ranked.append((team_names.get(team_id, team_id), pts, seen_scores[pts]))
        pos = i + 2  # next position accounts for current index (1-based)

    # Determine tie indicators
    ties: set[int] = set()
    for name, pts, rank in ranked:
        count = sum(1 for _, p, _ in ranked if p == pts)
        if count > 1:
            ties.add(rank)

    # Find highest week
    max_week = max(week_numbers) if week_numbers else "?"

    html = build_html(ranked, ties, max_week)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Wrote: {output_path}")
    return str(output_path)


def build_html(standings: list, ties: set[int], max_week: int) -> str:
    rows_html = ""
    for name, pts, rank in standings:
        pos_str = format_position(rank, ties)
        rank_class = f"rank-{rank}" if rank <= 3 else ""
        rows_html += f"""      <tr class="{rank_class}"><td class="td-pos">{pos_str}</td><td class="td-player">{name}</td><td class="td-total">{pts}</td></tr>\n"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Hickory Hills Men's League — Standings</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Helvetica, Arial, sans-serif;
    background: #0d2318;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .wrapper {{
    width: 7.5in;
    background: #fff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    padding: 18px 24px 20px;
  }}
  .header {{
    text-align: center;
    padding-bottom: 12px;
    border-bottom: 2px solid #0d2318;
    margin-bottom: 12px;
  }}
  .league-name {{
    font-size: 13pt;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #0d2318;
  }}
  .subtitle {{
    font-size: 9pt;
    font-weight: 400;
    color: #666;
    margin-top: 2px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  thead th {{
    background: #0d2318;
    color: #d4af37;
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 5px 8px;
    border: 1px solid #0d2318;
  }}
  thead th.pos-col {{ text-align: left; width: 40px; }}
  thead th.player-col {{ text-align: left; }}
  thead th.total-col {{ text-align: center; width: 68px; }}
  tbody tr {{ border-bottom: 1px solid #dcdcdc; }}
  tbody tr:nth-child(even) {{ background: #f6f6f6; }}
  tbody td {{
    padding: 4px 8px;
    font-size: 9pt;
    color: #111;
    vertical-align: middle;
  }}
  tbody td.td-pos {{
    font-size: 10pt;
    font-weight: 900;
    color: #0d2318;
    text-align: left;
  }}
  tr.rank-1 td.td-pos {{ color: #8b7000; }}
  tr.rank-2 td.td-pos {{ color: #666; }}
  tr.rank-3 td.td-pos {{ color: #8b5000; }}
  tbody td.td-player {{ font-weight: 700; font-size: 9.5pt; }}
  tbody td.td-total {{
    text-align: center;
    font-size: 11pt;
    font-weight: 900;
    color: #0d2318;
  }}
  tr.rank-1 td.td-total {{ color: #8b7000; }}
  tr.rank-2 td.td-total {{ color: #666; }}
  tr.rank-3 td.td-total {{ color: #8b5000; }}
  tr.rank-1 {{ background: #fdf5e0; }}
  tr.rank-2 {{ background: #f4f4f4; }}
  tr.rank-3 {{ background: #faf5ef; }}
  .footer-note {{
    margin-top: 10px;
    font-size: 7pt;
    color: #aaa;
    text-align: center;
  }}
  @media print {{
    body {{ background: white; padding: 0; }}
    @page {{ size: letter; margin: 0.2in; }}
    .wrapper {{ box-shadow: none; width: 7.5in; padding: 10px 16px; }}
    tbody tr:nth-child(even) {{ background: #f6f6f6; }}
    tr.rank-1, tr.rank-2, tr.rank-3 {{ background: inherit !important; }}
  }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="league-name">Hickory Hills Wednesday Night Men's League</div>
    <div class="subtitle">Season Standings — Through Week {max_week}</div>
  </div>
  <table>
    <thead>
      <tr>
        <th class="pos-col">Pos</th>
        <th class="player-col">Team</th>
        <th class="total-col">Total Pts</th>
      </tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>
  <div class="footer-note">Hickory Hills Wednesday Night Men's League 2026</div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    generate_leaderboard()
