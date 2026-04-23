# Scorecard Automation — SPEC

## Concept & Vision
Generate print-ready PDF scorecards for a Wednesday night golf league at Hickory Hills GC. Each scorecard covers the front 9 only. Cards are dropped into a printer tray — clean, professional, exactly how Josh wants them.

## The Scorecard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HICKORY HILLS GOLF COURSE  ·  Week 2  ·  Apr 22, 2026         │
├──────────────┬────┬────┬────┬────┬────┬────┬────┬────┬────────┤
│              │ H1 │ H2 │ H3 │ H4 │ H5 │ H6 │ H7 │ H8 │ H9     │ ← hole numbers
│              │SI  │SI  │SI  │SI  │SI  │SI  │SI  │SI  │SI      │ ← stroke index
│              │Par │Par │Par │Par │Par │Par │Par │Par │Par     │ ← par per hole
├──────────────┼────┴────┴────┴────┴────┴────┴────┴────┴────────┤
│ PLAYER NAME  │  ●   ●       ●   ●       ●       ●    ●       │ ← strokes (● = stroke hole)
│ Hdcp: ##.#   │                                                │
├──────────────┼────┬────┬────┬────┬────┬────┬────┬────┬────────┤
│ PLAYER NAME  │  ●       ●   ●       ●   ●       ●    ●       │
│ Hdcp: ##.#   │                                                │
└──────────────┴────┴────┴────┴────┴────┴────┴────┴────┴────────┘

(Repeat for second matchup on same card)

┌─────────────────────────────────────────────────────────────────┐
│ MATCHUP 2                                                      │
├──────────────┬────┬────┬────┬────┬────┬────┬────┬────┬────────┤
│ PLAYER NAME  │  ●   ●       ●   ●       ●       ●    ●       │
│ Hdcp: ##.#   │                                                │
├──────────────┼────┬────┬────┬────┬────┬────┬────┬────┬────────┤
│ PLAYER NAME  │  ●       ●   ●       ●   ●       ●    ●       │
│ Hdcp: ##.#   │                                                │
└──────────────┴────┴────┴────┴────┴────┴────┴────┴────┴────────┘
```

## Key Specs
- **Format:** 8.5" × 11" landscape, 2 matchups per card (4 players)
- **Course:** Hickory Hills GC, front 9 only
- **Par:** 33 (4+3+4+4+3+4+3+4+4)
- **Stroke Index:** [4,7,2,6,8,5,9,1,3] per hole
- **Player row height:** room for a filled-in score
- **Stroke dots:** solid filled circle, positioned in the grid cell

## Matchup Logic
- From Team Matchplay CSV section: top 2 players in a group play each other, bottom 2 play each other
- Strokes = floor((high_hdcp - low_hdcp) / 2)
- Strokes allocated starting at SI 1 (hardest) hole and counting up
- Dots shown on ALL strokes (not just first few — if a player gets 5 strokes, dots appear on the 5 hardest holes)
- Lower HDCP player is marked with "(fav)" label on their row

## Input
- Drop squabbit CSV into `input/`
- Run: `python generate_scorecards.py`
- PDFs land in `output/`

## Output
- One PDF per group (4 players, 2 matchups)
- Filename: `Week_X_Scorecards_HickoryHills.pdf`
- Print-ready, no color ink needed (black text + gray grid + filled dots)

## Stack
- **HTML/CSS** → scorecard template
- **WeasyPrint** → HTML to PDF conversion
- **Python csv module** → CSV parsing