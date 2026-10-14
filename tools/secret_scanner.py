"""
community_hub/tools/secret_scanner.py
Scan text, files, and directories for exposed secrets, API keys, tokens, and credentials.
Includes patterns for AWS, GitHub, OpenAI, Slack, Google, Stripe, SSH private keys, and high-entropy strings.
"""

import os
import re
import math
from typing import Dict, Any, List, Optional


SECRET_PATTERNS = [
    {
        "name": "AWS Access Key",
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b",
        "severity": "CRITICAL"
    },
    {
        "name": "AWS Secret Key",
        "pattern": r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "severity": "CRITICAL"
    },
    {
        "name": "GitHub Personal Access Token",
        "pattern": r"\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b",
        "severity": "CRITICAL"
    },
    {
        "name": "GitHub OAuth Token",
        "pattern": r"\b(gho_[0-9a-zA-Z]{36}|ghs_[0-9a-zA-Z]{36})\b",
        "severity": "CRITICAL"
    },
    {
        "name": "OpenAI / Anthropic API Key",
        "pattern": r"\b(sk-[a-zA-Z0-9]{20,T3BlbkFJ[a-zA-Z0-9]{20,}|sk-ant-[a-zA-Z0-9_\-]{40,})\b",
        "severity": "CRITICAL"
    },
    {
        "name": "Slack Bot / User Token",
        "pattern": r"\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32})\b",
        "severity": "HIGH"
    },
    {
        "name": "Slack Webhook URL",
        "pattern": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
        "severity": "HIGH"
    },
    {
        "name": "Stripe API Key",
        "pattern": r"\b(sk_live_[0-9a-zA-Z]{24}|rk_live_[0-9a-zA-Z]{24})\b",
        "severity": "CRITICAL"
    },
    {
        "name": "Google API Key",
        "pattern": r"\b(AIza[0-9A-Za-z\-_]{35})\b",
        "severity": "HIGH"
    },
    {
        "name": "RSA / OpenSSH Private Key",
        "pattern": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "severity": "CRITICAL"
    },
    {
        "name": "Generic Password / Secret in Code",
        "pattern": r"(?i)(password|secret|api_key|access_token)\s*[:=]\s*['\"]([^'\"]{8,64})['\"]",
        "severity": "MEDIUM"
    }
]


def _shannon_entropy(data: str) -> float:
    """Calculates the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy


def _mask_secret(secret: str) -> str:
    """Masks secret keeping only first 3 and last 3 characters."""
    if len(secret) <= 8:
        return "***"
    return secret[:3] + "*" * (len(secret) - 6) + secret[-3:]


def scan_content(content: str, source_label: str = "text") -> List[Dict[str, Any]]:
    """Scan string content for secrets and high-entropy tokens."""
    findings = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, 1):
        # 1. Pattern checks
        for rule in SECRET_PATTERNS:
            for match in re.finditer(rule["pattern"], line):
                raw_token = match.group(0)
                # Ignore common false positives
                if any(fp in raw_token.lower() for fp in ("example", "your_", "dummy", "placeholder", "xxx")):
                    continue
                findings.append({
                    "source": source_label,
                    "line": line_idx,
                    "type": rule["name"],
                    "severity": rule["severity"],
                    "masked_secret": _mask_secret(raw_token),
                    "snippet": line[:100].strip()
                })

        # 2. High-entropy token check on suspicious assigned strings
        assign_match = re.search(r"['\"]([a-zA-Z0-9_\-+/=]{24,80})['\"]", line)
        if assign_match:
            candidate = assign_match.group(1)
            entropy = _shannon_entropy(candidate)
            # Threshold for random cryptographic keys is usually > 4.2
            if entropy > 4.5 and not any(f["line"] == line_idx for f in findings):
                findings.append({
                    "source": source_label,
                    "line": line_idx,
                    "type": "High-Entropy Cryptographic Token",
                    "severity": "HIGH",
                    "entropy": round(entropy, 2),
                    "masked_secret": _mask_secret(candidate),
                    "snippet": line[:100].strip()
                })

    return findings


def secret_scanner(
    target: str,
    is_raw_text: bool = False,
    max_files: int = 200
) -> Dict[str, Any]:
    """
    Main entrypoint: Scans raw text, a single file, or a directory for exposed secrets.

    Args:
        target: Raw text content or path to a file/directory.
        is_raw_text: Set True if target is a raw text string, False if path.
        max_files: Maximum files to scan when target is a directory.
    """
    if is_raw_text:
        findings = scan_content(target, source_label="raw_text")
        return {
            "success": True,
            "target": "raw_text",
            "findings_count": len(findings),
            "findings": findings
        }

    abs_path = os.path.abspath(target)
    if not os.path.exists(abs_path):
        return {"success": False, "error": f"Path '{target}' not found."}

    all_findings = []
    scanned_files = 0

    if os.path.isfile(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                all_findings.extend(scan_content(f.read(), source_label=target))
            scanned_files = 1
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Directory walk
        for root, dirs, files in os.walk(abs_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "dist", "build")]
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                # Skip known binary extensions
                if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".tar", ".gz", ".exe", ".pyc"):
                    continue

                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, abs_path)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        file_findings = scan_content(f.read(), source_label=rel_path)
                        all_findings.extend(file_findings)
                    scanned_files += 1
                    if scanned_files >= max_files:
                        break
                except Exception:
                    continue
            if scanned_files >= max_files:
                break

    return {
        "success": True,
        "target": target,
        "scanned_files": scanned_files,
        "findings_count": len(all_findings),
        "clean": len(all_findings) == 0,
        "findings": all_findings
    }
