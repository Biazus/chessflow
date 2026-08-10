from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True, index=True)  # Mudei para nullable=True

    depth = Column(Integer, nullable=False)
    best_move = Column(String, nullable=True)
    evaluation = Column(Float, nullable=True)
    is_mate = Column(Integer, nullable=True)
    top_moves = Column(JSON, nullable=True)
    processing_time = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    position = relationship("Position", back_populates="analysis")