# Golf League Database Schema

## Tables

### Players

- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- handicap (REAL DEFAULT 0.0)
- phone (TEXT) -- Contact phone number
- email (TEXT) -- Contact email address
- address (TEXT) -- Mailing address
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### Teams

- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- player1_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Players(id))
- player2_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Players(id))
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### Courses

- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- location (TEXT)
- par_63 (BOOLEAN DEFAULT 1)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### Course_Holes

- id (INTEGER PRIMARY KEY)
- course_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Courses(id))
- hole_number (INTEGER NOT NULL) -- 1-9
- par (INTEGER NOT NULL)
- stroke_index (INTEGER NOT NULL) -- 1-9, where 1 is hardest
- UNIQUE(course_id, hole_number)
- UNIQUE(course_id, stroke_index)

### Seasons

- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL) -- e.g., "2026 Season"
- course_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Courses(id))
- start_date (DATE)
- end_date (DATE)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### Season_Teams

- id (INTEGER PRIMARY KEY)
- season_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Seasons(id))
- team_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Teams(id))
- UNIQUE(season_id, team_id)

### Matches

- id (INTEGER PRIMARY KEY)
- season_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Seasons(id))
- week_number (INTEGER NOT NULL) -- 1-25
- team1_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Teams(id))
- team2_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Teams(id))
- date_played (DATE)
- UNIQUE(season_id, week_number, team1_id, team2_id)
- UNIQUE(season_id, week_number, team2_id, team1_id) -- prevents duplicate scheduling

### Match_Scores

- id (INTEGER PRIMARY KEY)
- match_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Matches(id))
- team_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Teams(id))
- player1_gross_9 (INTEGER) -- front 9 gross score
- player2_gross_9 (INTEGER) -- front 9 gross score
- team_total_gross_9 (INTEGER) -- sum of both players
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### Hole_Scores

- id (INTEGER PRIMARY KEY)
- match_score_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Match_Scores(id))
- hole_number (INTEGER NOT NULL) -- 1-9
- player1_gross (INTEGER)
- player2_gross (INTEGER)
- player1_net (INTEGER)
- player2_net (INTEGER)
- hole_points (REAL) -- points earned for this hole (0, 0.5, or 1 per player)

### Team_Points

- id (INTEGER PRIMARY KEY)
- match_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Matches(id))
- team_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Teams(id))
- hole_points_total (REAL DEFAULT 0.0)
- team_bonus_points (REAL DEFAULT 0.0)
- total_points (REAL DEFAULT 0.0)

### Handicap_History

- id (INTEGER PRIMARY KEY)
- player_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Players(id))
- season_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES Seasons(id))
- week_number (INTEGER NOT NULL)
- handicap_value (REAL NOT NULL)
- calculated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- UNIQUE(player_id, season_id, week_number)

## Indexes

- Index on Teams(player1_id, player2_id) for quick lookup
- Index on Matches(season_id, week_number) for schedule viewing
- Index on Match_Scores(match_id, team_id) for score retrieval
- Index on Handicap_History(player_id, season_id, week_number) for handicap progression
