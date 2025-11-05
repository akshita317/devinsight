from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.services.github_service import github_service
from app.models.repository import Repository
from pydantic import BaseModel

router = APIRouter()

class RepositoryCreate(BaseModel):
    owner: str
    repo: str

class RepositoryResponse(BaseModel):
    id: int
    name: str
    owner: str
    full_name: str
    description: str | None
    url: str
    health_score: float
    open_issues_count: int
    open_prs_count: int
    stars: int
    language: str | None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=RepositoryResponse)
async def add_repository(repo_data: RepositoryCreate, db: Session = Depends(get_db)):
    """Add a new repository to monitor"""
    try:
        # Check if already exists
        existing = db.query(Repository).filter(
            Repository.full_name == f"{repo_data.owner}/{repo_data.repo}"
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Repository already being monitored")
        
        # Fetch from GitHub
        repo_info = await github_service.get_repository_info(repo_data.owner, repo_data.repo)
        health_score = await github_service.calculate_health_score(repo_data.owner, repo_data.repo)
        prs = await github_service.get_open_pull_requests(repo_data.owner, repo_data.repo)
        
        # Save to database
        db_repo = Repository(
            name=repo_info["name"],
            owner=repo_info["owner"],
            full_name=repo_info["full_name"],
            description=repo_info["description"],
            url=repo_info["url"],
            language=repo_info["language"],
            stars=repo_info["stars"],
            forks=repo_info["forks"],
            health_score=health_score,
            open_issues_count=repo_info["open_issues"],
            open_prs_count=len(prs),
            last_analyzed=datetime.utcnow()
        )
        
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)
        
        return db_repo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[RepositoryResponse])
async def list_repositories(db: Session = Depends(get_db)):
    """List all monitored repositories"""
    repos = db.query(Repository).filter(Repository.is_monitored == True).all()
    return repos

@router.get("/{owner}/{repo}/health")
async def get_repository_health(owner: str, repo: str):
    """Get detailed health metrics for a repository"""
    try:
        health_score = await github_service.calculate_health_score(owner, repo)
        repo_info = await github_service.get_repository_info(owner, repo)
        prs = await github_service.get_open_pull_requests(owner, repo)
        commits = await github_service.get_recent_commits(owner, repo)
        
        return {
            "health_score": health_score,
            "repository": repo_info,
            "metrics": {
                "open_prs": len(prs),
                "recent_commits": len(commits),
                "stars": repo_info["stars"],
                "forks": repo_info["forks"]
            },
            "pull_requests": prs[:5],
            "commits": commits[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{repo_id}")
async def remove_repository(repo_id: int, db: Session = Depends(get_db)):
    """Stop monitoring a repository"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo.is_monitored = False
    db.commit()
    
    return {"message": "Repository removed from monitoring"}