"""
community_hub/plugins/dependency_guard/main.py
Scans project dependencies for pinning best practices.
"""

def check_deps(path: str = "requirements.txt") -> dict:
    """Flags unpinned packages in requirements.txt."""
    import os
    if not os.path.exists(path):
        return {"success": True, "message": "No requirements.txt found", "unpinned": []}
    unpinned = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "==" not in line and ">=" not in line:
                unpinned.append(line)
    return {"success": True, "unpinned_count": len(unpinned), "unpinned": unpinned}
