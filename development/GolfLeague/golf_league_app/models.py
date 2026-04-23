"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

# =============================================================================
# PLAYER MODELS
# =============================================================================
class PlayerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    handicap: float = Field(..., ge=0, le=36)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=200)

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    handicap: Optional[float] = Field(None, ge=0, le=36)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=200)

class PlayerResponse(PlayerBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =============================================================================
# TEAM MODELS
# =============================================================================
class TeamBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    player1_id: str
    player2_id: str
    team_number: Optional[int] = Field(None, ge=1)

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    team_number: Optional[int] = Field(None, ge=1)

class TeamResponse(TeamBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =============================================================================
# SEASON MODELS
# =============================================================================
class SeasonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    course_id: str = Field(default="default")

class SeasonCreate(SeasonBase):
    pass

class SeasonResponse(SeasonBase):
    id: str
    team_ids: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

# =============================================================================
# MATCH MODELS
# =============================================================================
class MatchBase(BaseModel):
    season_id: str
    week_number: int = Field(..., ge=1, le=25)
    team1_id: str
    team2_id: str
    date_played: Optional[str] = None  # YYYY-MM-DD format

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: str
    completed: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =============================================================================
# SCORE MODELS
# =============================================================================
class ScoreSubmission(BaseModel):
    match_id: str
    team1_player1_scores: Dict[int, int] = Field(..., description="Gross scores for Team1 Player1, keys 1-9")
    team1_player2_scores: Dict[int, int] = Field(..., description="Gross scores for Team1 Player2, keys 1-9")
    team2_player1_scores: Dict[int, int] = Field(..., description="Gross scores for Team2 Player1, keys 1-9")
    team2_player2_scores: Dict[int, int] = Field(..., description="Gross scores for Team2 Player2, keys 1-9")

class HoleResult(BaseModel):
    hole: int
    stroke_index: int
    team1_p1_net: int
    team1_p2_net: int
    team2_p1_net: int
    team2_p2_net: int
    team1_p1_points: float
    team1_p2_points: float
    team2_p1_points: float
    team2_p2_points: float
    team1_points: float
    team2_points: float

class ScoreResponse(BaseModel):
    match_id: str
    team1_scores: Dict[str, Dict[int, int]]
    team2_scores: Dict[str, Dict[int, int]]
    team1_hole_points: float
    team2_hole_points: float
    team1_bonus: float
    team2_bonus: float
    team1_total: int
    team2_total: int
    team1_final_points: float
    team2_final_points: float
    winner: str
    hole_results: List[HoleResult]

# =============================================================================
# COURSE SETTINGS MODELS
# =============================================================================
class CourseSettingsResponse(BaseModel):
    stroke_index: List[int]
    hole_pars: Dict[int, int]
    course_name: str
    course_location: str

# =============================================================================
# STANDINGS MODELS
# =============================================================================
class TeamStandings(BaseModel):
    team_id: str
    team_name: str
    total_points: float
    matches_played: int
    matches_won: int
    matches_lost: int
    matches_tied: int

class StandingsResponse(BaseModel):
    season_id: Optional[str] = None
    standings: List[TeamStandings]
