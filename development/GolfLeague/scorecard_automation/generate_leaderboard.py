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


def parse_standings(csv_path: Path) -> list[dict]:
    """
    Parse the standings table from a Squabbit CSV export.
    Returns [{pos, team, total}, ...]
    """
    lines = csv_path.read_text(encoding="utf-8", errors="replace").split('\n')

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

    # Build rows
    rows_html = ""
    medal_icon = {
        'rank1': '🏆',
        'rank2': '🥈',
        'rank3': '🥉',
    }
    for i, row in enumerate(rows):
        rank = i + 1
        pos = row['pos']
        team = row['team']
        total = row['total']

        rank_class = f"rank-{rank}" if rank <= 3 else ""

        # Medal emoji for top 3
        medal = medal_icon.get(rank_class, '')

        rows_html += f"""      <tr class="{rank_class}">
        <td class="td-pos">{pos}{medal}</td>
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
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #0a1f14;
    padding: 28px 16px 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
  }}

  /* ── Trophy Banner ── */
  .trophy-banner {{
    text-align: center;
    margin-bottom: 18px;
    user-select: none;
  }}
  .trophy-banner .trophy-icon {{
    font-size: 44px;
    line-height: 1;
    display: block;
    margin-bottom: 4px;
  }}
  .trophy-banner h1 {{
    font-size: 11pt;
    font-weight: 900;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #d4af37;
    margin: 0 0 2px;
  }}
  .trophy-banner .season-label {{
    font-size: 8.5pt;
    color: #5a8a6a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}

  /* ── Card ── */
  .wrapper {{
    width: 7.5in;
    background: #ffffff;
    border-radius: 14px;
    box-shadow:
      0 2px 4px rgba(0,0,0,0.12),
      0 8px 24px rgba(0,0,0,0.35),
      0 24px 60px rgba(0,0,0,0.25);
    overflow: hidden;
  }}

  /* ── Card Header ── */
  .card-header {{
    background: linear-gradient(135deg, #0d2318 0%, #1a3d2a 100%);
    padding: 20px 24px 18px;
    position: relative;
    overflow: hidden;
  }}
  .card-header::before {{
    content: '';
    position: absolute;
    top: -40px;
    right: -20px;
    width: 140px;
    height: 140px;
    background: radial-gradient(circle, rgba(212,175,55,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }}
  .card-header::after {{
    content: '';
    position: absolute;
    bottom: -30px;
    left: -10px;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, rgba(212,175,55,0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }}
  .card-header-inner {{
    position: relative;
    z-index: 1;
  }}
  .card-header h2 {{
    font-size: 15pt;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 0.04em;
    margin: 0 0 3px;
  }}
  .card-header .card-subtitle {{
    font-size: 8.5pt;
    color: #7ab892;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0;
  }}
  .gold-divider {{
    height: 3px;
    background: linear-gradient(90deg, transparent, #d4af37 20%, #d4af37 80%, transparent);
    margin: 0;
  }}

  /* ── Table ── */
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  thead tr {{
    background: #0d2318;
  }}
  thead th {{
    color: #d4af37;
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 7px 12px;
    border: none;
    text-align: center;
  }}
  thead th.pos-col {{ text-align: left; width: 52px; }}
  thead th.team-col {{ text-align: left; }}
  thead th.total-col {{ width: 88px; }}

  tbody tr {{ border-bottom: 1px solid #ececec; }}
  tbody tr:nth-child(even) {{ background: #f7f9f7; }}
  tbody td {{
    padding: 6px 12px;
    font-size: 10pt;
    color: #1a1a1a;
    vertical-align: middle;
  }}

  /* Pos */
  tbody td.td-pos {{
    font-size: 10.5pt;
    font-weight: 800;
    color: #2c2c2c;
    text-align: left;
  }}

  /* Team name */
  tbody td.td-team {{
    font-weight: 600;
    font-size: 10.5pt;
    color: #1a2e1a;
    letter-spacing: 0.01em;
  }}

  /* Total */
  tbody td.td-total {{
    text-align: center;
    font-size: 12.5pt;
    font-weight: 900;
    color: #0d2318;
  }}

  /* ── Rank Highlights ── */
  tr.rank-1 td.td-pos {{ color: #b8860b; }}
  tr.rank-1 td.td-total {{ color: #b8860b; }}
  tr.rank-1 {{
    background: linear-gradient(90deg, #fffbeb 0%, #fffdf5 100%) !important;
    border-left: 3px solid #d4af37;
  }}

  tr.rank-2 td.td-pos {{ color: #607d8b; }}
  tr.rank-2 td.td-total {{ color: #607d8b; }}
  tr.rank-2 {{
    background: linear-gradient(90deg, #f5f5f5 0%, #fafafa 100%) !important;
    border-left: 3px solid #90a4ae;
  }}

  tr.rank-3 td.td-pos {{ color: #8b6914; }}
  tr.rank-3 td.td-total {{ color: #8b6914; }}
  tr.rank-3 {{
    background: linear-gradient(90deg, #fdf6ec 0%, #fffdf8 100%) !important;
    border-left: 3px solid #c89b3a;
  }}

  /* Ties — italic style */
  tr[class*="T"] td.td-pos {{
    font-style: italic;
  }}
  tr[class*="T"] td.td-team {{
    font-style: italic;
    color: #3a5a3a;
  }}

  /* ── Footer ── */
  .card-footer {{
    background: #0d2318;
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .card-footer .footer-left {{
    font-size: 7pt;
    color: #5a8a6a;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }}
  .card-footer .footer-right {{
    font-size: 7pt;
    color: #3d6652;
    letter-spacing: 0.04em;
  }}

  /* ── Print ── */
  @media print {{
    body {{ background: white; padding: 0; }}
    @page {{ size: letter; margin: 0.25in; }}
    .wrapper {{
      box-shadow: none;
      border-radius: 0;
      width: 100%;
    }}
    tr.rank-1, tr.rank-2, tr.rank-3 {{
      background: inherit !important;
    }}
    .card-header::before, .card-header::after {{ display: none; }}
  }}
</style>
</head>
<body>

  <!-- Trophy Banner -->
  <div class="trophy-banner">
    <span class="trophy-icon">🏆</span>
    <h1>Season Standings</h1>
    <div class="season-label">Week {week_count} &nbsp;·&nbsp; 2026</div>
  </div>

  <!-- Card -->
  <div class="wrapper">
    <div class="card-header">
      <div class="card-header-inner">
        <h2>{league_name}</h2>
        <p class="card-subtitle">Wednesday Night Men's Golf League</p>
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
    rows = parse_standings(csv_path)
    if not rows:
        raise ValueError("No standings data found in CSV")

    # Detect week count from data
    week_count = 3
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