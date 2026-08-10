from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class GameResult(str, enum.Enum):
    WHITE_WIN = "white_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"
    UNKNOWN = "unknown"

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    pgn = Column(Text, nullable=False)
    white_player = Column(String, nullable=True)
    black_player = Column(String, nullable=True)
    result = Column(Enum(GameResult), default=GameResult.UNKNOWN)
    eco_code = Column(String, nullable=True, index=True)  # Classificação de abertura
    opening_name = Column(String, nullable=True)

    # Movimentos em formato JSON para queries rápidas
    moves = Column(JSON, nullable=True)  # ["e2e4", "c7c5", ...]

    played_at = Column(DateTime, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow)
    analysis_status = Column(String, default="pending")  # pending, analyzing, completed, failed TODO melhorar

    user = relationship("User", back_populates="games")
    positions = relationship("Position", back_populates="game", cascade="all, delete-orphan")