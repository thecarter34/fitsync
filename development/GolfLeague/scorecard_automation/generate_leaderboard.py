#!/usr/bin/env python3
"""
Generate season standings leaderboard HTML from a Squabbit CSV export.
Reads the standings section (Pos, Player, Week 1, Week 2, Week 3, Total)
and produces a print-ready, single-page HTML leaderboard.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def parse_standings(csv_path: Path) -> tuple[list[dict], int]:
    """
    Parse the standings table from a Squabbit CSV export.
    Returns ([{pos, team, total}, ...], detected_week).
    Detects the actual latest played week by checking which week column has data.
    """
    lines = csv_path.read_text(encoding="utf-8", errors="replace").split('\n')

    header_idx = -1
    week_header_count = 3
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Pos,") or "Week 1" in stripped:
            header_idx = i
            if "Week 3" in stripped:
                week_header_count = 3
            elif "Week 2" in stripped:
                week_header_count = 2
            break

    if header_idx == -1:
        raise ValueError(f"Could not find standings header in {csv_path.name}")

    # Detect actual latest week from first few data rows.
    # Header columns: Pos(0), Player(1), Week1(2), Week2(3), Week3(4), Total(5)
    # Week 3 data lives in parts[4], Week 2 in parts[3].
    # If parts[4] has non-empty/non-"0" data → week 3 is active.
    # Otherwise check parts[3] → week 2.
    latest_week = 1
    for line in lines[header_idx + 1: header_idx + 10]:
        line = line.strip()
        if not line or line.startswith("Round") or line.startswith("Hickory"):
            break
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 6:
            continue
        week3_val = parts[4] if len(parts) > 4 else ''
        week2_val = parts[3] if len(parts) > 3 else ''
        if week3_val and week3_val != '0':
            latest_week = 3
            break
        elif week2_val and week2_val != '0':
            latest_week = 2

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

    return rows, latest_week


def build_html(rows: list[dict], output_path: Path, week_count: int = 3) -> str:
    league_name = "Hickory Hills Golf Course"
    as_of = f"Standings end of week {week_count}"

    rows_html = ""
    for i, row in enumerate(rows):
        rank = i + 1
        pos = row['pos']
        team = row['team']
        total = row['total']
        rank_class = f"rank-{rank}" if rank <= 3 else ""
        rows_html += f"""<tr class="{rank_class}"><td class="td-pos">{pos}</td><td class="td-team">{team}</td><td class="td-total">{total}</td></tr>\n"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Hickory Hills Men's League — Standings</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #0a1f14;
    padding: 16px 20px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
  }}

  /* ── Trophy Banner ── */
  .trophy-banner {{
    text-align: center;
    margin-bottom: 8px;
    user-select: none;
  }}
  .trophy-banner .trophy-icon {{
    font-size: 28px;
    line-height: 1;
    display: block;
    margin-bottom: 2px;
  }}
  .trophy-banner h1 {{
    font-size: 9pt;
    font-weight: 900;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #d4af37;
    margin: 0 0 2px;
  }}
  .trophy-banner .as-of {{
    font-size: 7pt;
    color: #5a8a6a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-style: italic;
  }}

  /* ── Card ── */
  .wrapper {{
    width: 100%;
    background: #ffffff;
    border-radius: 10px;
    box-shadow:
      0 2px 4px rgba(0,0,0,0.10),
      0 8px 24px rgba(0,0,0,0.35),
      0 24px 60px rgba(0,0,0,0.25);
    overflow: hidden;
  }}

  /* ── Card Header ── */
  .card-header {{
    background: linear-gradient(135deg, #0d2318 0%, #1a3d2a 100%);
    padding: 14px 20px 12px;
    position: relative;
    overflow: hidden;
  }}
  .card-header::before {{
    content: '';
    position: absolute;
    top: -30px;
    right: -10px;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, rgba(212,175,55,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }}
  .card-header-inner {{ position: relative; z-index: 1; }}
  .card-header h2 {{
    font-size: 14pt;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 0.04em;
    margin: 0 0 2px;
  }}
  .card-header .card-subtitle {{
    font-size: 7.5pt;
    color: #7ab892;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 2px;
  }}
  .gold-divider {{
    height: 2px;
    background: linear-gradient(90deg, transparent, #d4af37 20%, #d4af37 80%, transparent);
  }}

  /* ── Table ── */
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }}
  thead tr {{ background: #0d2318; }}
  thead th {{
    color: #d4af37;
    font-size: 6.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    padding: 5px 10px;
    border: none;
  }}
  thead th.pos-col {{ text-align: left; width: 44px; }}
  thead th.team-col {{ text-align: left; }}
  thead th.total-col {{ text-align: center; width: 80px; }}

  tbody tr {{ border-bottom: 1px solid #ebebeb; }}
  tbody tr:nth-child(even) {{ background: #f3f6f3; }}
  tbody td {{
    padding: 3px 10px;
    font-size: 9pt;
    color: #111;
    vertical-align: middle;
  }}
  tbody td.td-pos {{
    font-size: 9pt;
    font-weight: 700;
    color: #1a2e1a;
    text-align: left;
    white-space: nowrap;
  }}
  tbody td.td-team {{
    font-weight: 600;
    font-size: 9.5pt;
    color: #1a2e1a;
    letter-spacing: 0.01em;
  }}
  tbody td.td-total {{
    text-align: center;
    font-size: 10.5pt;
    font-weight: 800;
    color: #0d2318;
  }}

  /* ── Rank 1-3: bold only ── */
  tr.rank-1 td.td-pos, tr.rank-2 td.td-pos, tr.rank-3 td.td-pos {{ font-weight: 900; }}
  tr.rank-1 td.td-total, tr.rank-2 td.td-total, tr.rank-3 td.td-total {{ font-weight: 800; }}

  /* Ties */
  tr[class*="T"] td.td-pos {{ font-style: italic; }}
  tr[class*="T"] td.td-team {{ font-style: italic; color: #2d4f2d; }}

  /* ── Footer ── */
  .card-footer {{
    background: #0d2318;
    padding: 7px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .card-footer .footer-left {{ font-size: 6pt; color: #5a8a6a; letter-spacing: 0.06em; text-transform: uppercase; }}
  .card-footer .footer-right {{ font-size: 6pt; color: #3d6652; letter-spacing: 0.04em; }}

  /* ── Print: Portrait, single page ── */
  @page {{ size: portrait letter; margin: 0.2in; }}
  @media print {{
    body {{ background: white; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .wrapper {{ box-shadow: none; border-radius: 0; width: 100%; }}
    .trophy-banner {{ margin-bottom: 5px; }}
    .trophy-banner .trophy-icon {{ font-size: 22px; }}
    tr.rank-1, tr.rank-2, tr.rank-3 {{ background: inherit !important; }}
    .card-header::before {{ display: none; }}
    table {{ table-layout: fixed; }}
    thead th {{ font-size: 7pt; padding: 4px 8px; }}
    tbody td {{ padding: 2.5px 8px; font-size: 9pt; }}
    tbody td.td-team {{ font-size: 9.5pt; }}
    tbody td.td-total {{ font-size: 10.5pt; }}
  }}
</style>
</head>
<body>

  <!-- Trophy Banner -->
  <div class="trophy-banner">
    <span class="trophy-icon">🏆</span>
    <h1>Season Standings</h1>
    <div class="as-of">{as_of}</div>
  </div>

  <!-- Card -->
  <div class="wrapper">
    <div class="card-header">
      <div class="card-header-inner">
        <h2>{league_name}</h2>
        <p class="card-subtitle">Standings end of week {week_count}</p>
      </div>
    </div>
    <div class="gold-divider"></div>

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
      <span class="footer-right">Generated {__import__('datetime').date.today().strftime('%b %d, %Y')}</span>
    </div>
  </div>

</body>
</html>"""


def run(csv_path: Path) -> str:
    rows, week_count = parse_standings(csv_path)
    if not rows:
        raise ValueError("No standings data found in CSV")
    output_path = OUTPUT_DIR / "leaderboard.html"
    html = build_html(rows, output_path, week_count)
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_leaderboard.py <csv_path>")
        sys.exit(1)
    run(Path(sys.argv[1]))