from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Opponent(Base):
    __tablename__ = "opponents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)

    games_against = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

    weaknesses = Column(JSON, nullable=True)  # {"openings": ["e4"], "tactics": "weak_in_endgame"}
    preferred_openings = Column(JSON, nullable=True)  # ["e4", "d4"]

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="opponents")