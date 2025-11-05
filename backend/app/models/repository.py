from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from datetime import datetime
from app.core.database import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    owner = Column(String(255), index=True)
    full_name = Column(String(512), unique=True, index=True)
    description = Column(Text, nullable=True)
    url = Column(String(512))
    
    # Metadata
    language = Column(String(100), nullable=True)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    
    # Health metrics
    health_score = Column(Float, default=0.0)
    open_issues_count = Column(Integer, default=0)
    open_prs_count = Column(Integer, default=0)
    security_alerts_count = Column(Integer, default=0)
    
    # Tracking
    is_monitored = Column(Boolean, default=True)
    last_analyzed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Repository {self.full_name}>"