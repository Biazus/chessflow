from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.game import GameResult
from app.schemas.position import PositionResponse

class GameBase(BaseModel):
    white_player: Optional[str] = None
    black_player: Optional[str] = None
    result: GameResult = GameResult.UNKNOWN

class GameCreate(GameBase):
    pgn: str

class GameUpdate(BaseModel):
    result: Optional[GameResult] = None
    elo_rating: Optional[int] = None

class GameResponse(GameBase):
    id: int
    eco_code: Optional[str] = None
    opening_name: Optional[str] = None
    moves: Optional[List[str]] = None
    analysis_status: str
    imported_at: datetime

    class Config:
        from_attributes = True

class GameDetailResponse(GameResponse):
    pgn: str
    played_at: Optional[datetime] = None
    positions: List[PositionResponse] = []