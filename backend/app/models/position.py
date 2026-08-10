from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)

    fen = Column(String, nullable=False, index=True)  # Forsyth-Edwards Notation
    move_number = Column(Integer, nullable=False)  # Número do movimento
    move_san = Column(String, nullable=False)  # Notação algébrica (e.g., "e4")

    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="positions")
    analysis = relationship("Analysis", back_populates="position", uselist=False, cascade="all, delete-orphan")