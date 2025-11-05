from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.repository import Repository

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics overview"""
    repos = db.query(Repository).filter(Repository.is_monitored == True).all()
    
    total_repos = len(repos)
    avg_health_score = sum(r.health_score for r in repos) / total_repos if total_repos > 0 else 0
    total_issues = sum(r.open_issues_count for r in repos)
    total_prs = sum(r.open_prs_count for r in repos)
    
    return {
        "total_repositories": total_repos,
        "average_health_score": round(avg_health_score, 2),
        "total_open_issues": total_issues,
        "total_open_prs": total_prs,
        "repositories": [
            {
                "name": r.full_name,
                "health_score": r.health_score,
                "issues": r.open_issues_count,
                "prs": r.open_prs_count
            }
            for r in repos
        ]
    }