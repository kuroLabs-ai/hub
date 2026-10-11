"""
community_hub/tools/regex_tester.py
Regular Expression testing utility for KuroCode.
"""

def regex_tester(pattern: str, text: str) -> dict:
    """Test a regular expression against text and return matches."""
    import re
    try:
        compiled = re.compile(pattern)
        matches = [m.group(0) for m in compiled.finditer(text)]
        return {
            "success": True,
            "pattern": pattern,
            "match_count": len(matches),
            "matches": matches[:50],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
