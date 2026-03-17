from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .db import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    plan = Column(Text)
    observations = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
