# Golf League Manager - Web Application

A modern, mobile-responsive web application for managing your golf league. Built with FastAPI, Tailwind CSS, and Jinja2 templates.

## Features

- **Complete League Management**: Players, teams, seasons, matches, and standings
- **Mobile-Optimized Score Entry**: Large touch-friendly inputs for on-course scoring
- **Real-Time Calculations**: Automatic net score calculation with Hickory Hills stroke index
- **Schedule Generation**: Automated round-robin scheduling based on handicaps
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Docker Ready**: Easy deployment on NAS or any Docker host

## Quick Start

### Option 1: Docker (Recommended for NAS)

1. Ensure Docker and Docker Compose are installed on your NAS
2. Clone or copy this directory to your NAS
3. Edit `docker-compose.yml` to set the correct data volume path:
   ```yaml
   volumes:
     - /volume1/data/golf-league:/app/data # Adjust to your NAS path
   ```
4. Start the application:
   ```bash
   docker-compose up -d
   ```
5. Access at `http://your-nas-ip:1234`

### Option 2: Local Python

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Ensure the `data` directory exists and contains your JSON files:
   - `players.json`
   - `teams.json`
   - `matches.json`
   - `scores.json`
   - `course_settings.json`
   - `seasons.json`
   - `handicap_history.json`

3. Run the application:

   ```bash
   python main.py
   ```

4. Open browser to `http://localhost:1234`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile/Desktop Browser                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  HTML5 + Tailwind CSS (Jinja2 Templates)              │  │
│  │  - Dashboard, Players, Teams, Course Settings        │  │
│  │  - Season Setup, Schedule, Match Entry, Standings    │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (main.py)                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  GET  /api/players          - List all players        │  │
│  │  POST /api/players          - Create player           │  │
│  │  PUT  /api/players/{id}     - Update player           │  │
│  │  DELETE /api/players/{id}  - Delete player            │  │
│  │                                                       │  │
│  │  GET  /api/teams            - List all teams          │  │
│  │  POST /api/teams            - Create team             │  │
│  │                                                       │  │
│  │  GET  /api/matches          - List matches            │  │
│  │  POST /api/matches          - Create match            │  │
│  │  DELETE /api/matches/{id}  - Delete match             │  │
│  │                                                       │  │
│  │  POST /api/scores/submit    - Submit match scores     │  │
│  │  GET  /api/standings        - Team rankings           │  │
│  │  GET  /api/course-settings  - Course configuration    │  │
│  │  PUT  /api/course-settings  - Update settings         │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ Python imports
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Core Business Logic (Decoupled)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  data_manager.py                                      │  │
│  │  - JSON file I/O                                      │  │
│  │  - Player/Team/Season/Match management                │  │
│  │  - Schedule generation algorithms                     │  │
│  │  - Handicap tracking (rolling 3-week average)        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  scoring_engine.py                                    │  │
│  │  - Match-play scoring calculations                    │  │
│  │  - Hickory Hills stroke index allocation              │  │
│  │  - Net score, hole points, team bonus                 │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ File I/O
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              JSON Data Files (./data or /app/data)          │
│  players.json | teams.json | matches.json | scores.json    │
│  course_settings.json | seasons.json | handicap_history.json│
└─────────────────────────────────────────────────────────────┘
```

## API Documentation

### Players

- `GET /api/players` - List all players
- `GET /api/players/{id}` - Get player details
- `POST /api/players` - Create player (body: `PlayerCreate`)
- `PUT /api/players/{id}` - Update player (body: `PlayerUpdate`)
- `DELETE /api/players/{id}` - Delete player

### Teams

- `GET /api/teams` - List all teams
- `GET /api/teams/{id}` - Get team details
- `POST /api/teams` - Create team (body: `TeamCreate`)
- `PUT /api/teams/{id}` - Update team (body: `TeamUpdate`)
- `DELETE /api/teams/{id}` - Delete team

### Matches

- `GET /api/matches` - List all matches (query: `season_id`, `week`)
- `GET /api/matches/{id}` - Get match details
- `POST /api/matches` - Create match (body: `MatchCreate`)
- `DELETE /api/matches/{id}` - Delete match

### Schedule Generation

- `POST /api/schedule/generate` - Generate full season schedule
  - Body: `{ "season_id": "...", "team_ids": [...] }`
- `POST /api/schedule/generate-week` - Generate matches for a week
  - Body: `{ "season_id": "...", "week_number": 1 }`

### Scores

- `POST /api/scores/submit` - Submit hole-by-hole scores
  - Body: `ScoreSubmission` with gross scores for all 4 players
  - Returns calculated net scores, points, and winner

### Standings

- `GET /api/standings?season_id={id}` - Get team standings

### Course Settings

- `GET /api/course-settings` - Get stroke index, hole pars, scoring config
- `PUT /api/course-settings` - Update settings (partial update supported)

## Data Model

### Player

```json
{
  "id": "P...",
  "name": "John Doe",
  "handicap": 12.5,
  "phone": "...",
  "email": "...",
  "created_at": "2026-04-05T..."
}
```

### Team

```json
{
  "id": "T...",
  "name": "Doe-Smith",
  "player1_id": "P...",
  "player2_id": "P...",
  "team_number": 1
}
```

### Match

```json
{
  "id": "M...",
  "season_id": "S...",
  "week_number": 1,
  "team1_id": "T...",
  "team2_id": "T...",
  "date_played": "2026-04-05",
  "completed": false
}
```

### Match Scores (after submission)

```json
{
  "match_id": "M...",
  "team1_scores": { "player1": {1: 4, 2: 3, ...}, "player2": {...} },
  "team2_scores": { "player1": {...}, "player2": {...} },
  "team1_hole_points": 12.5,
  "team2_hole_points": 8.5,
  "team1_bonus": 5.0,
  "team2_bonus": 0.0,
  "team1_final_points": 17.5,
  "team2_final_points": 8.5,
  "winner": "team1",
  "hole_results": [...]
}
```

## Scoring System

### Hickory Hills Stroke Index

```
Hole:  1  2  3  4  5  6  7  8  9
SI:    3  7  1  6  8  5  9  2  4
```

### Match Play Rules

1. **Handicap Strokes**: Higher handicap player receives strokes equal to the difference between handicaps
2. **Stroke Allocation**: Strokes applied to hardest holes first (lowest SI = hardest)
3. **Net Score**: Gross - (1 if stroke_index <= handicap_diff else 0)
4. **Hole Points**: Winner of each matchup gets configured points (default 1.0). Ties = 0.
5. **Team Bonus**: Team with lower combined net score gets bonus points (default 5.0)
6. **Total Points**: Hole points + team bonus

### Example

- Player A (hcp 8) vs Player B (hcp 12): diff = 4
- Player B receives strokes on holes with SI <= 4: holes 3 (SI=1), 4 (SI=6? no), 8 (SI=2), 9 (SI=4)
- Actually: SI order [3,7,1,6,8,5,9,2,4] → holes with SI<=4: hole 3 (SI=1), hole 8 (SI=2), hole 9 (SI=4) = 3 strokes

## Mobile-First Design

The Match Entry page is optimized for on-course scoring:

- Large, easy-to-tap score inputs
- Visual stroke hole highlighting (orange background)
- Side-by-side player comparison
- Real-time results modal with detailed hole-by-hole breakdown
- Works offline (data saved to server)

## Docker Deployment on Synology NAS

1. **Prepare the data directory**:

   ```bash
   # On your NAS, create a directory for persistent data
   mkdir -p /volume1/data/golf-league
   ```

2. **Copy existing data** (if migrating from desktop):

   ```bash
   # Copy your existing data/ folder to the NAS directory
   ```

3. **Edit docker-compose.yml**:

   ```yaml
   volumes:
     - /volume1/data/golf-league:/app/data
   ```

4. **Deploy**:

   ```bash
   docker-compose up -d
   ```

5. **Access**: Open `http://your-nas-ip:8000` in any browser

6. **Backup**: Regularly backup the `/volume1/data/golf-league` directory

## Environment Variables

- `DATA_DIR`: Path to data directory (default: `/app/data` in Docker, `data` locally)
- `ENVIRONMENT`: Set to `production` for Docker

## Development

### Project Structure

```
golf-league-web/
├── main.py              # FastAPI application
├── data_manager.py      # Data persistence layer
├── scoring_engine.py    # Scoring calculations
├── models.py            # Pydantic models
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
├── data/                # JSON data files (mounted volume)
│   ├── players.json
│   ├── teams.json
│   ├── matches.json
│   ├── scores.json
│   ├── course_settings.json
│   ├── seasons.json
│   └── handicap_history.json
└── templates/           # Jinja2 HTML templates
    ├── base.html
    ├── index.html (Dashboard)
    ├── players.html
    ├── teams.html
    ├── course_settings.html
    ├── season_setup.html
    ├── schedule.html
    ├── match_entry.html
    └── standings.html
```

### Running Tests

```bash
python test_decoupled.py
```

This tests that `data_manager.py` and `scoring_engine.py` work independently.

## Migration from Desktop App

1. **Data Compatibility**: The web app uses the exact same JSON file format as the desktop Tkinter app
2. **No Conversion Needed**: Simply copy your existing `data/` folder to the web app's data directory
3. **Same Logic**: All scoring calculations, schedule generation, and handicap tracking are identical
4. **Parallel Operation**: You can run both desktop and web apps simultaneously during transition

## Troubleshooting

### Port Already in Use

Change the port in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000" # Access on port 8001
```

### Data Not Persisting

Check that the volume mount in `docker-compose.yml` points to a valid directory on your NAS. The container writes to `/app/data` internally.

### Permission Errors

Ensure the NAS directory has write permissions for the Docker container. On Synology:

```bash
sudo chmod -R 755 /volume1/data/golf-league
```

### API Errors

Check the container logs:

```bash
docker-compose logs golf-league
```

## License

MIT License - Same as original desktop application

## Support

For issues or questions, refer to the original application documentation or create an issue in the repository.
