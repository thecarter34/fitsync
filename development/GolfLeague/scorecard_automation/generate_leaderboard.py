#!/usr/bin/env python3
"""
Generate season standings leaderboard HTML from a Squabbit CSV export.
Reads the standings section (Pos, Player, Week 1, Week 2, Week 3, Total)
and produces a print-ready HTML page with Pos, Team, Total columns.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def parse_standings(csv_path: Path) -> list[dict]:
    """
    Parse the standings table from a Squabbit CSV export.
    Returns [{pos, team, total}, ...]
    """
    lines = csv_path.read_text(encoding="utf-8", errors="replace").split('\n')

    # Find the standings header line
    header_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Pos,") or "Week 1" in stripped:
            header_idx = i
            break

    if header_idx == -1:
        raise ValueError(f"Could not find standings header in {csv_path.name}")

    rows = []
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line or line.startswith("Round") or line.startswith("Hickory"):
            break
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 6:
            continue
        pos = parts[0].strip()
        team = parts[1].strip()
        try:
            total = float(parts[-1].strip())
        except ValueError:
            continue
        rows.append({'pos': pos, 'team': team, 'total': total})

    return rows


def build_html(rows: list[dict], output_path: Path, week_count: int = 3) -> str:
    league_name = "Hickory Hills Wednesday Night Men's League"

    rows_html = ""
    for i, row in enumerate(rows):
        rank = i + 1
        pos = row['pos']
        team = row['team']
        total = row['total']

        rank_class = f"rank-{rank}" if rank <= 3 else ""
        rows_html += f"""      <tr class="{rank_class}">
        <td class="td-pos">{pos}</td>
        <td class="td-team">{team}</td>
        <td class="td-total">{total}</td>
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
    font-size: 7.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 6px 10px;
    border: 1px solid #0d2318;
    text-align: center;
  }}
  thead th.pos-col {{ text-align: left; width: 46px; }}
  thead th.team-col {{ text-align: left; }}
  thead th.total-col {{ width: 80px; }}
  tbody tr {{ border-bottom: 1px solid #dcdcdc; }}
  tbody tr:nth-child(even) {{ background: #f6f6f6; }}
  tbody td {{
    padding: 5px 10px;
    font-size: 10pt;
    color: #111;
    vertical-align: middle;
  }}
  tbody td.td-pos {{
    font-size: 11pt;
    font-weight: 900;
    color: #0d2318;
    text-align: left;
  }}
  tbody td.td-team {{ font-weight: 700; font-size: 10.5pt; }}
  tbody td.td-total {{
    text-align: center;
    font-size: 12pt;
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
    <div class="subtitle">Season Standings — Week {week_count}</div>
  </div>
  <table>
    <thead>
      <tr>
        <th class="pos-col">Pos</th>
        <th class="team-col">Team</th>
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


def run(csv_path: Path) -> str:
    rows = parse_standings(csv_path)
    if not rows:
        raise ValueError("No standings data found in CSV")

    output_path = OUTPUT_DIR / "leaderboard.html"
    html = build_html(rows, output_path)
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_leaderboard.py <csv_path>")
        sys.exit(1)
    run(Path(sys.argv[1]))