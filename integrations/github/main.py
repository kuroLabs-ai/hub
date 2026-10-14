"""
community_hub/integrations/github/main.py
GitHub REST API connector for repository details, issues, pull requests, and workflow dispatches.
"""

import os
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List, Optional


class GitHubConnector:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def _request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Dict[str, Any]:
        url = f"https://api.github.com/{endpoint.lstrip('/')}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "KuroCode-GitHub-Connector/1.0"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        body_bytes = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = resp.read().decode("utf-8")
                return {
                    "success": True,
                    "status_code": resp.getcode(),
                    "data": json.loads(resp_data) if resp_data else None
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repo metadata, stars, default branch."""
        return self._request(f"repos/{owner}/{repo}")

    def list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List open issues."""
        return self._request(f"repos/{owner}/{repo}/issues?state={state}")

    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict[str, Any]:
        """Create a new issue."""
        return self._request(f"repos/{owner}/{repo}/issues", method="POST", data={"title": title, "body": body})

    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List pull requests."""
        return self._request(f"repos/{owner}/{repo}/pulls?state={state}")


def main(action: str = "get_repo", **kwargs) -> Dict[str, Any]:
    connector = GitHubConnector()
    if hasattr(connector, action):
        func = getattr(connector, action)
        return func(**kwargs)
    return {"success": False, "error": f"Unknown GitHub action '{action}'"}
