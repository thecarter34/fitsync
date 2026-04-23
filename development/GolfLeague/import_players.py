#!/usr/bin/env python3
"""
Import script for golf league players from CSV data.
This script parses the provided CSV and creates players.json and teams.json.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Tuple

# Data file paths
DATA_DIR = "data"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def generate_team_name(player1_name: str, player2_name: str) -> str:
    """Generate a team name from the last names of two players."""
    p1_name = player1_name.strip()
    p2_name = player2_name.strip()

    p1_parts = p1_name.split()
    p2_parts = p2_name.split()

    p1_last = p1_parts[-1] if p1_parts else ""
    p2_last = p2_parts[-1] if p2_parts else ""

    if p1_last and p2_last:
        return f"{p1_last}-{p2_last}"
    elif p1_last:
        return p1_last
    elif p2_last:
        return p2_last
    else:
        return "Team"

def parse_csv_data(csv_text: str) -> Dict[int, List[Dict]]:
    """Parse CSV text and group players by team number."""
    lines = csv_text.strip().split('\n')
    teams = {}

    # Skip header line
    for line in lines[1:]:
        # Parse CSV line - handle quoted fields
        parts = []
        in_quotes = False
        current = ""
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                parts.append(current)
                current = ""
            else:
                current += char
        parts.append(current)

        if len(parts) < 6:
            continue

        team_num = int(parts[0].strip())
        name = parts[1].strip().strip('"')
        phone = parts[2].strip().strip('"')
        avg = parts[3].strip()
        hcap = parts[4].strip()
        points = parts[5].strip()

        # Parse "Lastname, Firstname" format to "Firstname Lastname"
        if ',' in name:
            lastname, firstname = name.split(',', 1)
            full_name = f"{firstname.strip()} {lastname.strip()}"
            lastname_clean = lastname.strip()
        else:
            full_name = name
            lastname_clean = name.split()[-1] if name.split() else ""

        player = {
            "name": full_name,
            "phone": phone if phone else "",
            "handicap": float(hcap) if hcap else 0.0,
            "lastname": lastname_clean
        }

        if team_num not in teams:
            teams[team_num] = []
        teams[team_num].append(player)

    return teams

def create_players_and_teams(teams_data: Dict[int, List[Dict]]) -> Tuple[Dict, Dict]:
    """Create players and teams JSON structures."""
    players = {}
    teams = {}
    current_time = datetime.now().isoformat()

    for team_num, team_players in teams_data.items():
        if len(team_players) != 2:
            print(f"Warning: Team {team_num} has {len(team_players)} players (expected 2)")
            continue

        player1, player2 = team_players[0], team_players[1]

        # Create player entries
        for i, player in enumerate([player1, player2], 1):
            player_id = generate_id("P")
            players[player_id] = {
                "id": player_id,
                "name": player["name"],
                "handicap": player["handicap"],
                "phone": player["phone"],
                "email": "",
                "address": "",
                "created_at": current_time,
                "updated_at": current_time
            }
            # Store player_id for team creation
            if i == 1:
                player1_id = player_id
                player1_lastname = player.get("lastname", player["name"].split()[-1])
            else:
                player2_id = player_id
                player2_lastname = player.get("lastname", player["name"].split()[-1])

        # Create team entry using last names
        team_id = generate_id("T")
        team_name = f"{player1_lastname}-{player2_lastname}"
        teams[team_id] = {
            "id": team_id,
            "name": team_name,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "team_number": team_num,
            "created_at": current_time,
            "updated_at": current_time
        }

    return players, teams

def main():
    # CSV data from user
    csv_data = '''Team #,Name,Phone Number,Avg,HCap,Points
1,"Hanson, Gene",,42,8,0.0
1,"Topper, Brandon",,39,3,0.0
2,"Walker, Luke",(715)-210-5622,43,6,255.0
2,"Dodge, Jason",,38,1,255.0
3,"Steffen, Ben",(715)-379-4115,39,3,253.0
3,"Steffen, Bart",(715)-456-7868,37,5,253.0
4,"Hoyord, Chad",(715)-225-4830,43,7,246.5
4,"Wollum, Pete",(715)-491-0265,47,10,246.5
5,"Kelm, Dan",(715)-579-7923,38,5,241.0
5,"Holden, Jeff",(715)-214-3797,45,9,241.0
6,"Blackburn, Bill",(715)-456-6987,39,5,243.5
6,"Degrasse, Dave",(715)-215-1557,42,8,243.5
7,"Fladten, Craig (Whitey)",(715)-559-0177,40,4,220.0
7,"Everhart, Dan",(715)-456-6984,45,11,0.0
8,"Johnson, Marquell",,43,6,213.0
8,"Hill, Frank",(715)-533-5618,40,6,213.0
9,"Maher, Steve",(715)-559-4411,45,9,225.0
9,"Fladten, Matt",(715)-492-1371,34,0,225.0
10,"Malnory, Mark",(715)-379-3926,43,10,227.5
10,"Freseth, Curt",(715)-829-8477,44,9,227.5
11,"Brantner, Bill",,41,7,218.0
11,"Ehrhard, Mike",(715)-828-1993,54,17,218.0
12,"VanderWegen, Matt",(715)-379-7068,36,2,225.5
12,"Carter, Josh",(715)-828-6179,46,7,225.5
13,"Sorenson, Scott",,45,10,214.5
13,"Biermeier, Frank",(715)-563-7011,50,12,214.5
14,"Wold, Jim",,48,11,212.5
14,"Anderson, Rick",(715)-271-5431,45,10,212.5
15,"Tyler, Bob",(715)-828-8334,47,13,207.5
15,"Sorenson, Dan",,43,9,207.5
16,"Welke, Dennis",(715)-210-5527,48,12,158.0
16,"Berg, Travis",,41,4,205.0
17,"Thompson, Darren",,50,12,202.0
17,"Kjelstad, Kerry",,48,10,202.0
18,"Bilyeu, Mike",,49,13,205.5
18,"Young, Terry",,45,7,205.5
19,"Schretenthaler, Keith",(715)-829-6812,46,11,209.0
19,"Schretenthaler, Sam",(715)-497-7619,0,18,0.0
20,"Christy, Darrell",(715)-579-6180,55,17,198.5
20,"Blattner, Craig",,48,9,198.5
21,"Nussbaum, Jeff",,47,8,207.5
21,"Carlson, Randy",(715)-559-3305,47,10,207.5
22,"Sessions, Joe",(715)-829-0986,49,12,209.0
22,"Plomedahl, Dan",(715)-538-3238,43,6,209.0
23,"Verbracken, Brandon",,45,11,216.5
23,"Larson, Ryan",,42,7,216.5'''

    print("Parsing CSV data...")
    teams_data = parse_csv_data(csv_data)

    print(f"Found {len(teams_data)} teams")
    for team_num, players_list in sorted(teams_data.items()):
        print(f"  Team {team_num}: {len(players_list)} players")
        for p in players_list:
            print(f"    - {p['name']} (HCap: {p['handicap']}, Phone: {p['phone'] or 'N/A'})")

    print("\nCreating players and teams...")
    players, teams = create_players_and_teams(teams_data)

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save players.json
    with open(PLAYERS_FILE, 'w') as f:
        json.dump(players, f, indent=2, default=str)
    print(f"Saved {len(players)} players to {PLAYERS_FILE}")

    # Save teams.json
    with open(TEAMS_FILE, 'w') as f:
        json.dump(teams, f, indent=2, default=str)
    print(f"Saved {len(teams)} teams to {TEAMS_FILE}")

    print("\nImport complete!")

if __name__ == "__main__":
    main()
