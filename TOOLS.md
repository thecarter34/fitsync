# TOOLS.md - Local Notes

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

---

# CODING SETUP (Josh)

## Editor & Workflow
- **Editor:** VS Code with Roo Coder extension
- **Style:** Vibe coding — stack-agnostic, whatever works best for the task
- **Philosophy:** No rigid stack. Pick the right tool per project.

## Workspace Structure
```
development/
├── CarterQualityConstruction/   # Active project (construction co. website)
├── GolfLeague/                   # Golf league management app (Josh's project)
├── fitness/                      # Gym/health tracking
└── [future projects]
```

## Projects

- **CarterQualityConstruction** — `/workspace/development/CarterQualityConstruction/` | `http://localhost:8080` | tmux session: `dev-servers:cqc`
- **GolfLeague** — `/workspace/development/GolfLeague/`
- **Mission Control** — `/workspace/mission_control/` | `http://localhost:5050` | General-purpose automation dashboard

## Dev Servers (tmux: dev-servers)

Dev servers run in a persistent tmux session called `dev-servers`. This keeps them alive between turns.

**Managing dev servers:**
```bash
# List running servers
tmux list-windows -t dev-servers

# Check server output
tmux capture-pane -t dev-servers -p

# Kill a server
tmux kill-window -t dev-servers:PROJECT_NAME
```

**Starting a new dev server:**
```bash
# From project directory, e.g.:
cd /home/thecarter34/.openclaw/workspace/development/CarterQualityConstruction
python3 -m http.server 8080
# Then: Ctrl+B, D to detach (or just let me background it)
```

## Browser Testing
- Browser plugin is configured for localhost testing
- I can open pages, take screenshots, click around, fill forms, verify changes

## Key Commands I Should Know
- Run dev server: `python3 -m http.server PORT` or project-specific (Vite, Next.js, etc.)
- Open in browser: browser tool (headless or headed)
- File edits: direct read/write/edit in `/home/thecarter34/.openclaw/workspace/development/`

## Stack-Agnostic Approach
- Plain HTML/CSS/JS → fast, simple, no build step
- Need a framework? → suggest one based on the task
- Database? → SQLite for lightweight, Postgres for real projects
- Hosting? → local dev first, then suggest deployment options