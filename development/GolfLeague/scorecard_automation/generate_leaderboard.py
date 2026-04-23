#!/usr/bin/env python3
"""
Generate season standings leaderboard HTML from golf league data.
Can read from:
  1. A Squabbit CSV export (standings section at bottom of file)
  2. Golf League app JSON data files (matches.json, scores.json, teams.json)

Produces a print-ready, single-page HTML leaderboard.
"""

import json
import sys
import re
from pathlib import Path
from collections import defaultdict
from datetime import date

# Default paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path("/home/thecarter34/.openclaw/workspace/development/GolfLeague/golf_league_app/data")
OUTPUT_DIR = SCRIPT_DIR / "output"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_position(rank: int, ties: set[int]) -> str:
    if rank in ties:
        return f"T{rank}"
    return str(rank)


def parse_standings_from_csv(csv_path: Path) -> tuple[list, int]:
    """
    Parse the standings table from a Squabbit CSV export.
    Returns ([(pos_str, team, total), ...], detected_week).
    The standings section starts after a blank row and begins with
    'Pos,Player,Week 1,...' header.
    """
    lines = csv_path.read_text(encoding="utf-8", errors="replace").split('\n')

    # Find the header row that starts the standings section
    header_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Pos,") or "Week 1" in stripped:
            header_idx = i
            break

    if header_idx < 0:
        raise ValueError("Could not find standings header row in CSV")

    # Determine how many week columns there are by parsing the header
    headers = lines[header_idx].strip().split(',')
    week_cols = []
    for idx, h in enumerate(headers):
        h_clean = h.strip()
        if h_clean.startswith("Week "):
            try:
                week_num = int(h_clean.replace("Week ", "").strip())
                week_cols.append((idx, week_num))
            except ValueError:
                pass

    # Find Total column index
    total_col = 5  # default based on format: Pos,Player,Week1,Week2,,Total
    for idx, h in enumerate(headers):
        if h.strip() == "Total":
            total_col = idx
            break

    # Determine the last week that actually has data
    # Count how many teams have scores in each week column
    # The week with the most scores is the most recently completed week
    week_score_counts: dict[int, int] = {}
    for col_idx, week_num in week_cols:
        week_score_counts[week_num] = 0

    for line in lines[header_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            break
        cols = stripped.split(',')
        for col_idx, week_num in week_cols:
            if col_idx < len(cols):
                cell = cols[col_idx].strip()
                # Real score has a space (two player scores like "5 7"), not just "0" or empty
                if cell and ' ' in cell:
                    week_score_counts[week_num] += 1

    # The most recently completed week: highest score count wins, ties go to the higher week number
    max_week = max(week_score_counts, key=lambda w: (week_score_counts[w], w))
    if max_week == 0:
        max_week = 1

    # Parse data rows until we hit an empty row or non-data row
    standings = []
    for line in lines[header_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            break
        cols = stripped.split(',')

        if len(cols) <= total_col:
            continue

        pos_str = cols[0].strip()
        team = cols[1].strip()
        total_str = cols[total_col].strip().rstrip(',')

        if not team or not pos_str:
            continue

        try:
            total = float(total_str)
        except ValueError:
            continue

        standings.append((pos_str, team, total))

    return standings, max_week


def generate_from_csv(
    csv_path: Path,
    output_path: Path = OUTPUT_DIR / "leaderboard.html",
) -> str:
    raw_rows, max_week = parse_standings_from_csv(csv_path)

    # raw_rows = [(pos_str, team, total), ...]
    # Build ranked list with computed positions, detect ties
    points_groups: dict[float, list] = defaultdict(list)
    for pos_str, team, total in raw_rows:
        points_groups[total].append((pos_str, team, total))

    # Sort by points descending
    sorted_groups = sorted(points_groups.items(), key=lambda x: -x[0])

    # Assign positions
    ranked = []
    ties: set[int] = set()
    pos = 1
    for total, group in sorted_groups:
        if len(group) > 1:
            for (pos_str, team, tot) in group:
                ties.add(pos)
                ranked.append((team, tot, pos_str))
            pos += len(group)
        else:
            pos_str, team, tot = group[0]
            ranked.append((team, tot, pos_str))
            pos += 1

    html = build_html(ranked, ties, max_week)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote: {output_path}")
    return str(output_path)


def generate_leaderboard(
    matches_path: Path = DATA_DIR / "matches.json",
    scores_path: Path = DATA_DIR / "scores.json",
    teams_path: Path = DATA_DIR / "teams.json",
    output_path: Path = OUTPUT_DIR / "leaderboard.html",
) -> str:
    matches = load_json(matches_path)
    scores = load_json(scores_path)
    teams = load_json(teams_path)

    team_points: dict[str, float] = defaultdict(float)
    team_names: dict[str, str] = {}

    for team_id, team_data in teams.items():
        team_names[team_id] = team_data["name"]
        team_points[team_id] = 0.0

    week_numbers: set[int] = set()

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

    standings_list = sorted(team_points.items(), key=lambda x: -x[1])

    seen_scores: dict[float, int] = {}
    ranked = []
    for i, (team_id, pts) in enumerate(standings_list):
        if pts not in seen_scores:
            seen_scores[pts] = i + 1
        ranked.append((team_names.get(team_id, team_id), pts, seen_scores[pts]))

    ties: set[int] = set()
    for name, pts, rank in ranked:
        count = sum(1 for _, p, _ in ranked if p == pts)
        if count > 1:
            ties.add(rank)

    max_week = max(week_numbers) if week_numbers else 1

    html = build_html(ranked, ties, max_week)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote: {output_path}")
    return str(output_path)


def build_html(standings: list, ties: set[int] | None, max_week: int) -> str:
    today = date.today().strftime("%b %d, %Y")

    rows_html = ""
    for entry in standings:
        if len(entry) == 3:
            # JSON mode: (name, pts, rank_int)
            # CSV mode: (team, total, pos_str) where pos_str is already formatted
            name, pts, third = entry
            if isinstance(third, int):
                # JSON mode — third is rank number
                pos_str = format_position(third, ties or set())
                rank = third
            else:
                # CSV mode — third is already a pos string like "T1", "3", etc.
                pos_str = third
                # Determine rank for CSS class (1, 2, 3)
                # Find the actual numeric rank from position string
                rank = int(third.replace('T', '')) if third.lstrip('T').isdigit() else 0
        else:
            name, pts = entry
            pos_str = ""
            rank = 0
        rank_class = f"rank-{rank}" if rank in (1, 2, 3) else ""
        rows_html += f'<tr class="{rank_class}"><td class="td-pos">{pos_str}</td><td class="td-team">{name}</td><td class="td-total">{pts}</td></tr>\n'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Hickory Hills Men's League — Standings</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #f4f6f4;
    padding: 16px 20px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
  }}
  .wrapper {{
    width: 100%;
    background: #ffffff;
    border-radius: 10px;
    box-shadow:
      0 2px 4px rgba(0,0,0,0.08),
      0 8px 24px rgba(0,0,0,0.12);
    overflow: hidden;
  }}
  .card-header {{
    background: #ffffff;
    padding: 14px 20px 12px;
    border-bottom: 3px solid #0d2318;
    position: relative;
  }}
  .card-header::before {{
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0d2318 0%, #1a3d2a 50%, #0d2318 100%);
  }}
  .card-header-inner {{ position: relative; z-index: 1; display: flex; justify-content: center; align-items: center; flex-direction: column; text-align: center; }}
  .card-header-titles {{ width: 100%; }}
  .card-header h2 {{ font-size: 16pt; font-weight: 900; color: #0d2318; letter-spacing: 0.04em; margin: 0 0 3px; }}
  .card-header .card-subtitle {{ font-size: 10pt; color: #3d6652; letter-spacing: 0.12em; text-transform: uppercase; margin: 0; }}
  .card-header .standings-date {{ font-size: 10pt; color: #0d2318; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; text-align: center; white-space: nowrap; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
  thead tr {{ background: #0d2318; }}
  thead th {{ color: #d4af37; font-size: 9pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; padding: 6px 10px; border: none; }}
  thead th.pos-col {{ text-align: left; width: 44px; }}
  thead th.team-col {{ text-align: left; }}
  thead th.total-col {{ text-align: center; width: 80px; }}
  tbody tr {{ border-bottom: 1px solid #ebebeb; }}
  tbody tr:nth-child(even) {{ background: #f3f6f3; }}
  tbody td {{ padding: 4px 10px; font-size: 11pt; color: #111; vertical-align: middle; }}
  tbody td.td-pos {{ font-size: 11pt; font-weight: 700; color: #1a2e1a; text-align: left; white-space: nowrap; }}
  tbody td.td-team {{ font-weight: 700; font-size: 12pt; color: #1a2e1a; letter-spacing: 0.01em; }}
  tbody td.td-total {{ text-align: center; font-size: 12pt; font-weight: 800; color: #0d2318; }}
  tr.rank-1 td.td-pos, tr.rank-2 td.td-pos, tr.rank-3 td.td-pos {{ font-weight: 900; }}
  tr.rank-1 td.td-total, tr.rank-2 td.td-total, tr.rank-3 td.td-total {{ font-weight: 800; }}
  tr[class*="T"] td.td-pos {{ font-style: italic; }}
  tr[class*="T"] td.td-team {{ font-style: italic; color: #2d4f2d; }}
  .card-footer {{ background: #ffffff; padding: 6px 20px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #ddd; }}
  .card-footer .footer-left {{ font-size: 6pt; color: #888; letter-spacing: 0.06em; text-transform: uppercase; }}
  .card-footer .footer-right {{ font-size: 6pt; color: #aaa; letter-spacing: 0.04em; }}
  @page {{ size: portrait letter; margin: 0.2in; }}
  @media print {{
    body {{ background: white; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .wrapper {{ box-shadow: none; border-radius: 0; width: 100%; }}
    .card-header {{ padding: 14px 20px 12px; }}
    .card-header::before {{ display: none; }}
    .card-header h2 {{ font-size: 16pt; }}
    .card-header .card-subtitle {{ font-size: 10pt; }}
    .card-header .standings-date {{ font-size: 10pt; }}
    tr.rank-1, tr.rank-2, tr.rank-3 {{ background: inherit !important; }}
    table {{ table-layout: fixed; }}
    thead th {{ font-size: 9pt; padding: 5px 8px; }}
    tbody td {{ padding: 4px 8px; font-size: 11pt; }}
    tbody td.td-pos {{ font-size: 11pt; }}
    tbody td.td-team {{ font-size: 12pt; font-weight: 700; }}
    tbody td.td-total {{ font-size: 12pt; }}
    .card-footer {{ padding: 8px 20px; }}
    .card-footer .footer-left, .card-footer .footer-right {{ font-size: 8pt; }}
  }}
</style>
</head>
<body>
  <div class="wrapper">
    <div class="card-header">
      <div class="card-header-inner">
        <div class="card-header-titles">
          <h2>Hickory Hills Golf Course</h2>
          <p class="card-subtitle">Wednesday Night Men's Golf League</p>
        </div>
        <div class="standings-date">Standings End<br>of Week {max_week}</div>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th class="pos-col">Pos</th>
          <th class="team-col">Team</th>
          <th class="total-col">Total Pts</th>
        </tr>
      </thead>
      <tbody>
{rows_html}      </tbody>
    </table>
    <div class="card-footer">
      <span class="footer-left">Hickory Hills GC &nbsp;·&nbsp; 2026 Season</span>
      <span class="footer-right">Generated {today}</span>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate season standings leaderboard HTML")
    parser.add_argument("--csv", type=Path, help="Path to Squabbit CSV export file")
    args = parser.parse_args()

    if args.csv:
        generate_from_csv(args.csv)
    else:
        generate_leaderboard()
