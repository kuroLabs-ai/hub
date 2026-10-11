"""
community_hub/tools/hash_calculator.py
Compute MD5, SHA1, SHA256, or SHA512 cryptographic checksums.
"""

def hash_calculator(text: str = "", algorithm: str = "sha256") -> dict:
    """Compute cryptographic hash of a given string."""
    import hashlib
    algo = algorithm.lower().strip()
    if algo not in hashlib.algorithms_available:
        return {"success": False, "error": f"Unsupported algorithm: {algo}"}
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return {
        "success": True,
        "algorithm": algo,
        "digest": h.hexdigest(),
        "length": len(text),
    }
