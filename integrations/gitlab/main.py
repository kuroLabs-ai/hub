"""
community_hub/integrations/gitlab/main.py
GitLab REST API connector for repository inspection, issue tracking, and CI/CD pipelines.
"""

import os
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List, Optional


class GitLabConnector:
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or os.environ.get("GITLAB_TOKEN", "")
        self.base_url = (base_url or os.environ.get("GITLAB_URL", "https://gitlab.com")).rstrip("/")

    def _request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Dict[str, Any]:
        if not self.token:
            return {"success": False, "error": "Missing GitLab token. Set GITLAB_TOKEN environment variable."}

        url = f"{self.base_url}/api/v4/{endpoint.lstrip('/')}"
        headers = {
            "PRIVATE-TOKEN": self.token,
            "User-Agent": "KuroCode-GitLab-Connector/1.0",
            "Content-Type": "application/json"
        }

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

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Fetch project details by ID or URL-encoded path."""
        encoded = urllib.parse.quote_plus(project_id)
        return self._request(f"projects/{encoded}")

    def list_issues(self, project_id: str, state: str = "opened") -> Dict[str, Any]:
        """List issues for a project."""
        encoded = urllib.parse.quote_plus(project_id)
        return self._request(f"projects/{encoded}/issues?state={state}")

    def list_pipelines(self, project_id: str) -> Dict[str, Any]:
        """List recent CI/CD pipelines."""
        encoded = urllib.parse.quote_plus(project_id)
        return self._request(f"projects/{encoded}/pipelines")


def main(action: str = "get_project", **kwargs) -> Dict[str, Any]:
    connector = GitLabConnector()
    if hasattr(connector, action):
        func = getattr(connector, action)
        return func(**kwargs)
    return {"success": False, "error": f"Unknown GitLab action '{action}'"}
