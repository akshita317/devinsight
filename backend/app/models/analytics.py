from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from datetime import datetime
from app.core.database import Base

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    
    # Metrics
    commit_count = Column(Integer, default=0)
    contributor_count = Column(Integer, default=0)
    avg_pr_merge_time = Column(Float, default=0.0)
    code_quality_score = Column(Float, default=0.0)
    
    # Additional data
    top_contributors = Column(Text, nullable=True)
    language_breakdown = Column(Text, nullable=True)
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    def __repr__(self):
        return f"<Analytics for repo_id={self.repository_id}>"