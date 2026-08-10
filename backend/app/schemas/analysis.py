from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class MoveEvaluation(BaseModel):
    move: str
    evaluation: Optional[float] = None
    mate: Optional[int] = None
    line: Optional[str] = None

class AnalysisBase(BaseModel):
    depth: int = 20

class AnalysisCreate(AnalysisBase):
    fen: str

class AnalysisResponse(AnalysisBase):
    id: int
    best_move: Optional[str] = None
    evaluation: Optional[float] = None
    is_mate: Optional[int] = None
    top_moves: Optional[List[Dict[str, Any]]] = None
    processing_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True