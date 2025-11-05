from github import Github
from app.core.config import settings
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        if settings.GITHUB_TOKEN:
            self.client = Github(settings.GITHUB_TOKEN)
        else:
            self.client = Github()
            logger.warning("GitHub token not set. Using unauthenticated access.")
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information"""
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            return {
                "name": repository.name,
                "owner": owner,
                "full_name": repository.full_name,
                "description": repository.description or "",
                "url": repository.html_url,
                "stars": repository.stargazers_count,
                "forks": repository.forks_count,
                "open_issues": repository.open_issues_count,
                "language": repository.language,
                "created_at": repository.created_at.isoformat() if repository.created_at else None,
                "updated_at": repository.updated_at.isoformat() if repository.updated_at else None,
            }
        except Exception as e:
            logger.error(f"Error fetching repository {owner}/{repo}: {str(e)}")
            raise Exception(f"Error fetching repository: {str(e)}")
    
    async def get_open_pull_requests(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get all open pull requests"""
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            pulls = repository.get_pulls(state='open')
            
            return [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login if pr.user else "unknown",
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "url": pr.html_url,
                }
                for pr in list(pulls)[:50]
            ]
        except Exception as e:
            logger.error(f"Error fetching PRs: {str(e)}")
            return []
    
    async def get_recent_commits(self, owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits"""
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            commits = list(repository.get_commits()[:limit])
            
            return [
                {
                    "sha": commit.sha[:7],
                    "message": commit.commit.message.split('\n')[0][:100],
                    "author": commit.commit.author.name if commit.commit.author else "unknown",
                    "date": commit.commit.author.date.isoformat() if commit.commit.author and commit.commit.author.date else None,
                    "url": commit.html_url,
                }
                for commit in commits
            ]
        except Exception as e:
            logger.error(f"Error fetching commits: {str(e)}")
            return []
    
    async def calculate_health_score(self, owner: str, repo: str) -> float:
        """Calculate repository health score (0-100)"""
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            
            score = 100.0
            
            # Deduct points for open issues
            open_issues = repository.open_issues_count
            score -= min(open_issues * 1, 20)
            
            # Check for recent activity
            try:
                last_commit = list(repository.get_commits()[:1])[0]
                days_since_commit = (datetime.now() - last_commit.commit.author.date.replace(tzinfo=None)).days
                if days_since_commit > 30:
                    score -= 15
                elif days_since_commit > 90:
                    score -= 30
            except:
                score -= 20
            
            # Check for documentation
            try:
                repository.get_contents("README.md")
                score += 10
            except:
                score -= 10
            
            # Check for license
            if repository.license:
                score += 5
            
            # Bonus for stars/community
            if repository.stargazers_count > 100:
                score += 10
            elif repository.stargazers_count > 10:
                score += 5
            
            return max(0, min(100, round(score, 2)))
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return 0.0

# Global instance
github_service = GitHubService()