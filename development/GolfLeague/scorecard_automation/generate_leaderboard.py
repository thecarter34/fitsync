#!/usr/bin/env python3
"""
Generate season standings leaderboard HTML from a Squabbit CSV export.
Extracts the standings table at the bottom of the CSV and produces a print-ready HTML page.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def parse_standings_from_csv(csv_path: Path) -> list[dict]:
    """
    Parse the standings section at the bottom of a Squabbit CSV export.
    Returns a list of dicts: {pos, team, week1, week2, week3, total}
    """
    content = csv_path.read_text(encoding="utf-8", errors="replace")

    # Find the standings section — look for the header line that starts with "Pos Player"
    lines = content.split('\n')
    standings_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('Pos ') or stripped.startswith('Pos,Player'):
            standings_start = i
            break

    if standings_start == -1:
        # Try to find by content pattern: lines that look like "T1 SomeName 5 7 5 13.5 36"
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and stripped.split()[0] in ('T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','1','2','3','4','5','6','7','8','9','10'):
                parts = [p.strip() for p in stripped.split()]
                if len(parts) >= 6:
                    try:
                        float(parts[-1])  # total should be numeric
                        standings_start = i
                        break
                    except ValueError:
                        continue

    if standings_start == -1:
        raise ValueError(f"Could not find standings section in {csv_path.name}")

    # Determine header offset
    header_line = lines[standings_start]
    stripped_header = header_line.strip()
    has_header = stripped_header.startswith('Pos')

    if has_header:
        data_start = standings_start + 1
    else:
        data_start = standings_start

    rows = []
    for line in lines[data_start:]:
        line = line.strip()
        if not line:
            continue
        # Skip separator lines or non-data lines
        if line.startswith('Round') or line.startswith('Hickory') or line.startswith('Week'):
            break
        # Parse: T1 Everhart/Fladten 5 7 5 13.5 36
        parts = line.split(',')
        if len(parts) < 2:
            continue

        pos_raw = parts[0].strip()
        team_raw = parts[1].strip()

        # Weekly points and total
        try:
            week1 = float(parts[2].strip()) if len(parts) > 2 and parts[2].strip() else 0.0
            week2 = float(parts[3].strip()) if len(parts) > 3 and parts[3].strip() else 0.0
            week3 = float(parts[4].strip()) if len(parts) > 4 and parts[4].strip() else 0.0
            total = float(parts[5].strip()) if len(parts) > 5 and parts[5].strip() else 0.0
        except ValueError:
            continue

        rows.append({
            'pos_raw': pos_raw,
            'team': team_raw,
            'week1': week1,
            'week2': week2,
            'week3': week3,
            'total': total,
        })

        if len(rows) >= 30:
            break

    return rows


def format_pos(pos_raw: str) -> str:
    """Return clean position string."""
    return pos_raw  # T1, T9, etc.


def build_html(rows: list[dict], output_path: Path) -> str:
    league_name = "Hickory Hills Wednesday Night Men's League"

    # Determine max week from data
    max_week = 3  # default
    for row in rows:
        if row['week2'] > 0:
            max_week = 3
            break
        elif row['week1'] > 0:
            max_week = 2
            break

    # Build HTML rows
    rows_html = ""
    for i, row in enumerate(rows):
        rank = i + 1
        pos = row['pos_raw']
        team = row['team']
        w1 = row['week1']
        w2 = row['week2']
        w3 = row['week3']
        total = row['total']

        rank_class = f"rank-{rank}" if rank <= 3 else ""
        rows_html += f"""      <tr class="{rank_class}">
        <td class="td-pos">{pos}</td>
        <td class="td-team">{team}</td>
        <td class="td-score">{format_score(w1)}</td>
        <td class="td-score">{format_score(w2)}</td>
        <td class="td-score">{format_score(w3)}</td>
        <td class="td-total">{format_score(total)}</td>
      </tr>\n"""

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
    padding-bottom: 10px;
    border-bottom: 2px solid #0d2318;
    margin-bottom: 10px;
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
    padding: 5px 6px;
    border: 1px solid #0d2318;
    text-align: center;
  }}
  thead th.pos-col {{ width: 38px; text-align: left; }}
  thead th.team-col {{ text-align: left; }}
  thead th.score-col {{ width: 54px; }}
  thead th.total-col {{ width: 60px; }}
  tbody tr {{ border-bottom: 1px solid #dcdcdc; }}
  tbody tr:nth-child(even) {{ background: #f6f6f6; }}
  tbody td {{
    padding: 4px 6px;
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
  tbody td.td-team {{ font-weight: 700; font-size: 9.5pt; }}
  tbody td.td-score {{
    text-align: center;
    font-size: 9pt;
  }}
  tbody td.td-total {{
    text-align: center;
    font-size: 11pt;
    font-weight: 900;
    color: #0d2318;
  }}
  tr.rank-1 td.td-pos {{ color: #8b7000; }}
  tr.rank-1 td.td-total {{ color: #8b7000; }}
  tr.rank-1 {{ background: #fdf5e0; }}
  tr.rank-2 td.td-pos {{ color: #555; }}
  tr.rank-2 td.td-total {{ color: #555; }}
  tr.rank-2 {{ background: #f4f4f4; }}
  tr.rank-3 td.td-pos {{ color: #8b5000; }}
  tr.rank-3 td.td-total {{ color: #8b5000; }}
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
    <div class="league-name">{league_name}</div>
    <div class="subtitle">Season Standings — Week {max_week}</div>
  </div>
  <table>
    <thead>
      <tr>
        <th class="pos-col">Pos</th>
        <th class="team-col">Team</th>
        <th class="score-col">Week 1</th>
        <th class="score-col">Week 2</th>
        <th class="score-col">Week 3</th>
        <th class="total-col">Total</th>
      </tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>
  <div class="footer-note">Hickory Hills Wednesday Night Men's League 2026</div>
</div>
</body>
</html>"""


def format_score(val: float) -> str:
    if val == 0.0:
        return "—"
    return str(val)


def run(csv_path: Path) -> str:
    rows = parse_standings_from_csv(csv_path)
    output_path = OUTPUT_DIR / "leaderboard.html"
    html = build_html(rows, output_path)
    output_path.write_text(html, encoding="utf-8")
    print(f"  Wrote: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Run on most recent CSV in input/
        input_dir = SCRIPT_DIR / "input"
        csv_files = sorted(input_dir.glob("*.csv"))
        if not csv_files:
            print("No CSV files found in input/")
            sys.exit(1)
        csv_path = csv_files[-1]
    else:
        csv_path = Path(sys.argv[1])

    run(csv_path)