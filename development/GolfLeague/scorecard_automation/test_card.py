#!/usr/bin/env python3
import generate_scorecards as g
import json

# Load existing data.json or create minimal one to test
data_path = g.INPUT_DIR / "Week_2_data.json"
csv_path = g.INPUT_DIR / "Week_2_April_22_2026.csv"

if data_path.exists():
    groups, week_num, date_str = g.load_data(data_path)
    players_hdcp = g.parse_players_hdcp(csv_path) if csv_path.exists() else {}
    print(f"Loaded Week {week_num} groups: {len(groups)}")
    cards = []
    for i, grp in enumerate(groups):
        enriched = []
        for p in grp["players"]:
            name = p["name"]
            strokes = p["strokes"]
            full_hdcp = players_hdcp.get(name, 0.0)
            enriched.append((name, full_hdcp, strokes))
        cards.append(g.build_card(i + 1, enriched, week_num, date_str, grp["hole"], "5:30 PM"))
    html = g.build_html(cards, week_num, date_str)
    out = g.OUTPUT_DIR / f"Week_{week_num}_print.html"
    with open(out, "w") as f:
        f.write(html)
    print(f"Saved: {out}")
else:
    print("No data.json found")
