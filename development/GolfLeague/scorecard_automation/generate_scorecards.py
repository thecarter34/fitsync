#!/usr/bin/env python3
"""
Scorecard Generator — PDF + CSV hybrid for Hickory Hills Golf Course.

PDF provides groups, hole assignments, tee times, and stroke allocations.
CSV provides 18-hole handicaps → 9-hole HDCP = round(full/2) shown in HDCP column.
"""

import csv
import re
from pathlib import Path

# ── Course config ────────────────────────────────────────────────────────────────
COURSE_NAME = "Hickory Hills Wednesday Night Men's League"
PAR = [4, 3, 4, 4, 3, 4, 3, 4, 4]
STROKE_INDEX = [4, 7, 2, 6, 8, 5, 9, 1, 3]
YARDAGES = [338, 158, 365, 268, 160, 289, 146, 330, 334]

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"


# ── CSV Parsing ─────────────────────────────────────────────────────────────────

def parse_players_hdcp(csv_path: Path) -> dict:
    """Extract name → 18-hole full handicap from Players section."""
    players = {}
    in_players = False
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            raw0 = row[0].strip() if row else ""
            if raw0.startswith("Players"):
                in_players = True
                continue
            if in_players:
                if raw0.startswith(("Team Matchplay", "Strokeplay", "Hickory")):
                    break
                if raw0 and len(row) >= 2:
                    try:
                        players[raw0] = float(row[1])
                    except:
                        pass
    return players


def short_name(full_name: str) -> str:
    """Extract last name from 'First Last' format."""
    parts = full_name.strip().split()
    return parts[-1] if parts else full_name


def nine_hdcp(full: float) -> int:
    """9-hole handicap = round(18-hole / 2)."""
    return round(full / 2)


# ── JSON Data Loading ───────────────────────────────────────────────────────────

def load_data(data_path: Path) -> tuple:
    """Load groups and meta from data.json."""
    import json
    with open(data_path) as f:
        data = json.load(f)
    week_num = data.get("week", "?")
    date_str = data.get("date", "?")
    groups = data.get("groups", [])
    return groups, week_num, date_str


# ── Stroke Logic ────────────────────────────────────────────────────────────────

def get_stroke_holes(stroke_count: int) -> list:
    """Return 0-based hole indices for a given stroke count, hardest-first."""
    if stroke_count <= 0:
        return []
    si_order = sorted(range(9), key=lambda i: STROKE_INDEX[i])
    return sorted(si_order[:stroke_count])


# ── HTML Building ────────────────────────────────────────────────────────────────

SCORECARD_CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; font-family: Helvetica, Arial, sans-serif; }
body { background: #1a3d2e; padding: 30px; margin: 0; min-height: 100vh; }
.paper { background: white; width: 8.5in; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.4); padding: 20px; }
.cards-wrapper { display: flex; flex-direction: column; gap: 15px; }
.card { width: 100%; height: auto; min-height: 4.5in; border: 1px solid #d4af37; padding: 0 12px 12px; }
.card-header { background: #1a3d2e; color: white; display: flex; justify-content: space-between; align-items: center; padding: 8px 12px 7px; border-bottom: 1px solid #d4af37; }
.course-name { font-size: 11pt; font-weight: 900; letter-spacing: 0.04em; text-transform: uppercase; color: #d4af37; }
.header-right { text-align: right; }
.week-info { font-size: 9pt; font-weight: 700; color: #d4af37; }
.group-info { font-size: 8.5pt; color: rgba(255,255,255,0.7); }
table.scorecard { width: 100%; border-collapse: collapse; }
col.name-col  { width: 62pt; }
col.h1-col, col.h2-col, col.h3-col, col.h4-col, col.h5-col, col.h6-col, col.h7-col, col.h8-col, col.h9-col { width: 30pt; }
col.out-col   { width: 34pt; }
col.hdcp-col  { width: 34pt; }
col.pts-col   { width: 48pt; }
table.scorecard td { border: 1px solid #222; text-align: center; vertical-align: middle; color: #111; height: 26pt !important; min-height: 26pt !important; padding: 1px 2px; font-size: 9pt; font-weight: 700; overflow: hidden; white-space: nowrap; }
table.scorecard tr { height: 26pt !important; }
table.scorecard td.row-label { background: #1a3d2e; color: #d4af37; font-size: 6.5pt; font-weight: 900; text-transform: uppercase; letter-spacing: 0.03em; text-align: left; padding: 1px 5px; border: 1px solid #222; border-right-color: #d4af37; }
table.scorecard td.hole-cell { background: #f0f8f5; color: #1a3d2e; font-size: 12pt; font-weight: 900; padding: 2px 0 1px; vertical-align: bottom; border: 1px solid #222; }
table.scorecard td.out-col { background: #e8f0ec; color: #1a3d2e; font-size: 7.5pt; font-weight: 900; border: 1px solid #222; }
table.scorecard td.hdcp-col { background: #e8f0ec; color: #1a3d2e; font-size: 7.5pt; font-weight: 900; border: 1px solid #222; }
table.scorecard td.pts-col { background: #e8f0ec; color: #1a3d2e; font-size: 7.5pt; font-weight: 900; border: 1px solid #222; }
table.scorecard td.player-name { background: #fff; color: #111; font-size: 9pt; font-weight: 800; text-align: left; padding: 2px 4px; vertical-align: middle; border: 1px solid #222; white-space: nowrap; overflow: hidden; }
table.scorecard td.stroke { background: #fff; color: #111; font-size: 5pt; font-weight: 700; vertical-align: top; padding-top: 2px; border: 1px solid #222; }
table.scorecard td.write { background: #fff; color: #111; font-size: 9pt; font-weight: 700; border: 1px solid #222; }
table.scorecard td.pts-cell { background: #fff; color: #111; font-size: 9pt; font-weight: 700; border: 1px solid #222; }
table.scorecard td.player-hdcp { background: #fff; color: #111; font-size: 9pt; font-weight: 700; border: 1px solid #222; }
/* Summary table at bottom of card — 6 columns: name + 5 data cells */
.summary-table { width: 100%; margin-top: 8px; border-collapse: collapse; border: 1px solid #222; }
table.summary-table td { border: 1px solid #222; text-align: center; vertical-align: top; color: #111; font-size: 7pt; font-weight: 700; padding: 2px 3px; }
table.summary-table td.sum-header-label { background: #1a3d2e; color: #d4af37; font-size: 6.5pt; font-weight: 900; text-transform: uppercase; text-align: left; padding: 1px 5px; border: 1px solid #222; border-right-color: #d4af37; }
table.summary-table td.sum-header { background: #e8f0ec; color: #1a3d2e; font-size: 7pt; font-weight: 900; padding: 2px 2px 1px; border: 1px solid #222; }
table.summary-table td.sum-team-name { background: #fff; color: #111; font-size: 8pt; font-weight: 800; text-align: left; padding: 2px 4px; border: 1px solid #222; white-space: nowrap; overflow: hidden; }
table.summary-table td.sum-cell { background: #fff; color: #111; border: 1px solid #222; }
.print-btn { display: block; margin: 20px auto; padding: 10px 28px; font-size: 14pt; font-weight: 700; background: #d4af37; color: #1a3d2e; border: none; border-radius: 6px; cursor: pointer; letter-spacing: 0.04em; text-transform: uppercase; }
.print-btn:hover { background: #b8962e; }
@media print {
  body { background: white; padding: 0; margin: 0; }
  .paper { box-shadow: none; width: 8.5in; margin: 0 auto; padding: 20px; }
  .print-btn { display: none; }
  @page { size: 8.5in 11in; margin: 0.4in; }
  .card { width: 100%; height: auto; min-height: 4.5in; border: 1px solid black; padding: 0 12px 12px; page-break-after: auto; page-break-inside: avoid; margin-bottom: 0.2in; }
  table.summary-table td.sum-header-label, table.summary-table td.sum-header { background: white !important; color: black !important; border: 1px solid black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  table.summary-table td.sum-team-name, table.summary-table td.sum-cell { background: white !important; color: black !important; border: 1px solid black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .card:last-child { margin-bottom: 0; }
  .card-header { background: white !important; color: black !important; border-bottom: 1px solid black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .course-name, .week-info, .group-info { color: black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  table.scorecard { width: 100%; border-collapse: collapse; }
  table.scorecard td { border: 1px solid black !important; color: black !important; background: white !important; height: 26pt !important; min-height: 26pt !important; overflow: hidden; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  table.scorecard tr { height: 26pt !important; }
  table.scorecard td.row-label { background: white !important; color: black !important; border: 1px solid black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}\
"""


def colgroup_html() -> str:
    cols = ['<col class="name-col" />']
    for i in range(1, 10):
        cols.append(f'<col class="h{i}-col" />')
    cols += ['<col class="out-col" />', '<col class="hdcp-col" />', '<col class="pts-col" />']
    return "\n              ".join(cols)


def header_row() -> str:
    holes = "".join(f'<td class="hole-cell">{h}</td>' for h in range(1, 10))
    return f'<tr><td class="row-label">Hole</td>{holes}<td class="out-col">Out</td><td class="hdcp-col">HDCP</td><td class="pts-col">Hole Pts</td></tr>'


def yardage_row() -> str:
    cells = "".join(f'<td>{y}</td>' for y in YARDAGES)
    return f'<tr><td class="row-label">Blue</td>{cells}<td class="out-col">{sum(YARDAGES)}</td><td class="hdcp-col"></td><td class="pts-col"></td></tr>'


def par_row() -> str:
    cells = "".join(f'<td>{p}</td>' for p in PAR)
    return f'<tr><td class="row-label">Par</td>{cells}<td class="out-col">{sum(PAR)}</td><td class="hdcp-col"></td><td class="pts-col"></td></tr>'


def si_row() -> str:
    cells = "".join(f'<td>{si}</td>' for si in STROKE_INDEX)
    return f'<tr><td class="row-label">SI</td>{cells}<td class="out-col">—</td><td class="hdcp-col"></td><td class="pts-col"></td></tr>'


def player_row(name: str, full_hdcp: float, stroke_count: int) -> str:
    """HDCP column shows 9-hole = round(full/2). Dots from stroke_count."""
    n9 = nine_hdcp(full_hdcp)
    stroke_holes = get_stroke_holes(stroke_count)
    cells = []
    for h in range(9):
        cls = "stroke" if h in stroke_holes else "write"
        dot = "●" if h in stroke_holes else ""
        cells.append(f'<td class="{cls}">{dot}</td>')
    return (
        f'<tr>'
        f'<td class="player-name">{name}</td>'
        + "".join(cells)
        + f'<td class="out-col"></td>'
        f'<td class="player-hdcp">{n9}</td>'
        f'<td class="pts-cell"></td>'
        f'</tr>'
    )


def build_card(group_num: int,
               players: list,      # [(name, full_hdcp, strokes), ...]
               week_num: str, date_str: str,
               hole_label: str, tee_time: str,
               teams_by_player: dict = None) -> str:
    # Determine actual teams from CSV team data
    if teams_by_player:
        # Use CSV team assignments: players on same team number are teammates
        player_teams = {}
        for p in players:
            t = teams_by_player.get(p[0], None)
            player_teams[p[0]] = t
        # Group by team number
        from collections import defaultdict
        team_groups = defaultdict(list)
        for p_data in players:
            t = player_teams.get(p_data[0], -1)
            if t is None:
                t = -1
            team_groups[t].append(p_data)
        team_list = list(team_groups.values())
        # Should have 2 teams; if more due to unmatched, merge into 2
        if len(team_list) == 2:
            team_a = team_list[0]
            team_b = team_list[1]
        elif len(team_list) > 2:
            # Merge unmatched/single players into nearest team
            team_a = team_list[0]
            team_b = team_list[1] if len(team_list) > 1 else team_list[0]
            for extra in team_list[2:]:
                if len(team_a) <= len(team_b):
                    team_a.append(extra[0])
                else:
                    team_b.append(extra[0])
        else:
            team_a = players[:2]
            team_b = players[2:]
    else:
        team_a = players[:2]
        team_b = players[2:]

    # Build display name from last names
    team_a_name = "/".join(sorted(short_name(p[0]) for p in team_a))
    team_b_name = "/".join(sorted(short_name(p[0]) for p in team_b))
    team_a_hdcp = sum(nine_hdcp(p[1]) for p in team_a)
    team_b_hdcp = sum(nine_hdcp(p[1]) for p in team_b)

    table_rows = "\n            ".join([
        header_row(),
        yardage_row(),
        par_row(),
        si_row(),
        *[player_row(name, full_hdcp, strokes) for name, full_hdcp, strokes in players],
    ])

    summary = f"""\
          <table class="summary-table">
            <colgroup>
              <col style="width: 62pt" />
              <col style="width: 55pt" />
              <col style="width: 55pt" />
              <col style="width: 55pt" />
              <col style="width: 55pt" />
              <col style="width: 55pt" />
              <col style="width: 56pt" />
            </colgroup>
            <tr>
              <td class="sum-header-label">Team</td>
              <td class="sum-header">Total<br/>Score</td>
              <td class="sum-header">Handicap</td>
              <td class="sum-header">Net<br/>Score</td>
              <td class="sum-header">Team<br/>Pts</td>
              <td class="sum-header">Hole<br/>Pts</td>
              <td class="sum-header">Total<br/>Points</td>
            </tr>
            <tr>
              <td class="sum-team-name">{team_a_name}</td>
              <td class="sum-cell"></td>
              <td class="sum-cell">{team_a_hdcp}</td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
            </tr>
            <tr>
              <td class="sum-team-name">{team_b_name}</td>
              <td class="sum-cell"></td>
              <td class="sum-cell">{team_b_hdcp}</td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
              <td class="sum-cell"></td>
            </tr>
          </table>"""

    return f"""\
        <div class="card">
          <div class="card-header">
            <span class="course-name">{COURSE_NAME}</span>
            <div class="header-right">
              <div class="week-info">Week {week_num} &nbsp;·&nbsp; {date_str}</div>
              <div class="group-info">Group {group_num} &nbsp;·&nbsp; Hole {hole_label} &nbsp;·&nbsp; {tee_time}</div>
            </div>
          </div>
          <table class="scorecard">
            <colgroup>
              {colgroup_html()}
            </colgroup>
            {table_rows}
          </table>
          {summary}
        </div>"""


def build_html(cards: list, week_num: str, date_str: str) -> str:
    return f"""\
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Hickory Hills Scorecards — Week {week_num}</title>
<style>
{SCORECARD_CSS}
</style>
</head>
<body>
<button class="print-btn" onclick="window.print()">Print Scorecards</button>
<div class="paper">
  <div class="cards-wrapper">
{"".join(cards)}
  </div>
</div>
</body>
</html>"""


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    # Look for data.json + any CSV with player HDCP data
    json_files = sorted(INPUT_DIR.glob("*_data.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    csv_files = sorted(INPUT_DIR.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)

    if not json_files:
        print("No _data.json found. Drop a PDF in and I'll process it first.")
        return

    data_path = json_files[0]
    csv_path = csv_files[0] if csv_files else None
    print(f"Processing: {data_path.name}" + (f" + {csv_path.name}" if csv_path else ""))

    groups, week_num, date_str = load_data(data_path)
    players_hdcp = parse_players_hdcp(csv_path) if csv_path else {}

    # Parse team matchplay from CSV to get teammate groupings
    teams_by_player = {}
    if csv_path and csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            lines = f.readlines()
        current_team = None
        for i in range(65, 150):
            line = lines[i].strip()
            if not line or line.startswith("Team Matchplay") or line.startswith("Team,Player"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if parts[0].isdigit() and all(p == "" for p in parts[1:]):
                current_team = int(parts[0])
            elif current_team is not None and parts[0] == "" and parts[1]:
                teams_by_player[parts[1]] = current_team

    print(f"  Week {week_num} · {date_str}")
    print(f"  Groups: {len(groups)}")
    for i, g in enumerate(groups):
        names = [p["name"] for p in g["players"]]
        strokes = [p["strokes"] for p in g["players"]]
        print(f"    Group {i+1} (Hole {g['hole']}, {g['time']}): {names} → strokes {strokes}")

    cards = []
    for i, g in enumerate(groups):
        enriched = []
        for p in g["players"]:
            name = p["name"]
            strokes = p["strokes"]
            full_hdcp = players_hdcp.get(name, 0.0)
            enriched.append((name, full_hdcp, strokes))
        cards.append(build_card(i + 1, enriched, week_num, date_str, g["hole"], "5:30 PM", teams_by_player))

    html_content = build_html(cards, week_num, date_str)

    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_week = week_num.replace("?", "unknown")
    html_path = OUTPUT_DIR / f"Week_{safe_week}_print.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  HTML: {html_path}")

    # Clean up — delete source files after successful generation
    for p in [data_path] + list(INPUT_DIR.glob("*.pdf")):
        if p.exists():
            p.unlink()
            print(f"  Cleaned up: {p.name}")


if __name__ == "__main__":
    main()
