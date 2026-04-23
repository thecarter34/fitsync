# UI Overhaul Setup - Parallel Development

## What Was Implemented

A `/new` subpath has been added to run a completely separate UI alongside the existing one without any impact.

## How to Access

- **Current UI (v1)**: `http://localhost:1234/`
  - Routes: `/`, `/players`, `/teams`, `/match-entry`, `/schedule`, `/standings`, `/course-settings`, `/season-setup`

- **New UI (v2)**: `http://localhost:1234/new`
  - Routes: `/new`, `/new/players`, `/new/teams`, `/new/match-entry`, `/new/schedule`, `/new/standings`, `/new/course-settings`, `/new/season-setup`

## File Structure

```
templates/
├── base.html                    # v1 base template
├── index.html                   # v1 dashboard
├── players.html                 # v1 players page
├── teams.html                   # v1 teams page
├── match_entry.html             # v1 match entry
├── schedule.html                # v1 schedule
├── standings.html               # v1 standings
├── course_settings.html         # v1 course settings
├── season_setup.html            # v1 season setup
│
└── new/                         # NEW UI templates
    ├── base.html                # Copy of v1 base (customize this)
    ├── index.html               # Copy of v1 dashboard (redesign here)
    ├── players.html             # Redesign players page
    ├── teams.html               # Redesign teams page
    ├── match_entry.html         # Redesign match entry
    ├── schedule.html            # Redesign schedule
    ├── standings.html           # Redesign standings
    ├── course_settings.html     # Redesign course settings
    └── season_setup.html        # Redesign season setup
```

## How to Develop

1. **Start the server**: `python main.py`
2. **Open browser**: Navigate to `http://localhost:1234/new` to see the new UI
3. **Edit templates**: Modify files in `templates/new/` to build your new design
4. **Both UIs share**: Same backend API, same database, same data layer
5. **Zero risk**: Changes to `templates/new/` don't affect the current UI at all

## When Ready to Launch

When the new UI is complete and tested, you have two options:

### Option A: Swap the routes (quick switch)

Update the existing routes in `main.py` to point to the new templates:

```python
# Change this:
return render_template("index.html", ...)
# To this:
return render_template("new/index.html", ...)
```

### Option B: Delete old templates (clean break)

1. Remove old template files (or move to `templates/v1/` backup)
2. Move `templates/new/` contents to root `templates/`
3. Remove the `/new` routes (or keep them as redirects)

## Notes

- Both UIs use the same API endpoints under `/api/*`
- Static assets are shared from `/static/`
- No database changes needed
- Session state is shared between both UIs
- You can customize `templates/new/base.html` to use a completely different design system

## Next Steps

Start customizing `templates/new/base.html` and `templates/new/index.html` with your new design!
