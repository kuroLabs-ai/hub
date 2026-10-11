"""
community_hub/plugins/code_metrics/main.py
Codebase metrics analyzer plugin.
"""

def analyze_metrics(path: str = ".") -> dict:
    """Calculates Python files and total lines of code in target path."""
    import os
    total_lines = 0
    files = 0
    for root, _, fnames in os.walk(path):
        for f in fnames:
            if f.endswith(".py"):
                files += 1
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fp:
                        total_lines += sum(1 for _ in fp)
                except Exception:
                    pass
    return {"success": True, "python_files": files, "total_lines": total_lines}
