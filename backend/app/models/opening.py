from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Opening(Base):
    __tablename__ = "openings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Informações da abertura
    name = Column(String, nullable=False)  # "Sicilian Defense"
    eco_code = Column(String, nullable=True, index=True)  # "B20"

    # Movimentos principais
    moves = Column(JSON, nullable=False)  # ["e2e4", "c7c5", ...]

    # Estatísticas
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    # Estudo
    studied_at = Column(DateTime, nullable=True)
    last_reviewed = Column(DateTime, nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="openings")