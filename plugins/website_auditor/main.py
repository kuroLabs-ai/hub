"""
community_hub/plugins/website_auditor/main.py
Audit web pages for SEO fundamentals, accessibility checks, performance bottlenecks, and security headers.
"""

from typing import Dict, Any, List
import urllib.request
import urllib.parse
import time
from html.parser import HTMLParser


class AuditHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: str = ""
        self.in_title: bool = False
        self.meta: Dict[str, str] = {}
        self.h1_count: int = 0
        self.h2_count: int = 0
        self.images_total: int = 0
        self.images_missing_alt: int = 0
        self.canonical_url: str = ""
        self.viewport_present: bool = False
        self.charset_present: bool = False
        self.favicon_present: bool = False
        self.internal_links: int = 0
        self.external_links: int = 0

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta":
            name = attr_dict.get("name") or attr_dict.get("property") or ""
            content = attr_dict.get("content") or ""
            if name and content:
                self.meta[name.lower()] = content
            if "viewport" in name.lower():
                self.viewport_present = True
            if "charset" in attr_dict or attr_dict.get("http-equiv", "").lower() == "content-type":
                self.charset_present = True
        elif tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            if "canonical" in rel:
                self.canonical_url = attr_dict.get("href", "")
            if "icon" in rel or "shortcut" in rel:
                self.favicon_present = True
        elif tag_lower == "h1":
            self.h1_count += 1
        elif tag_lower == "h2":
            self.h2_count += 1
        elif tag_lower == "img":
            self.images_total += 1
            if not attr_dict.get("alt"):
                self.images_missing_alt += 1
        elif tag_lower == "a":
            href = attr_dict.get("href", "")
            if href.startswith(("http://", "https://")):
                self.external_links += 1
            elif href and not href.startswith(("#", "javascript:")):
                self.internal_links += 1

    def handle_endtag(self, tag: str):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str):
        if self.in_title:
            self.title = (self.title + " " + data.strip()).strip()


def audit_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Audit a URL for SEO, accessibility, performance indicators, and security headers.
    """
    if not url.startswith(("http://", "https://")):
        return {"success": False, "error": "URL must begin with http:// or https://"}

    start_time = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KuroCode-WebsiteAuditor/1.0"
            }
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status_code = response.getcode()
            headers = dict(response.headers)
            content_bytes = response.read(1_500_000)

        html_text = content_bytes.decode("utf-8", errors="replace")
        parser = AuditHTMLParser()
        parser.feed(html_text)

        issues: List[Dict[str, str]] = []
        score = 100

        # SEO Checks
        title = parser.title
        if not title:
            issues.append({"category": "SEO", "severity": "HIGH", "message": "Missing <title> tag."})
            score -= 15
        elif len(title) < 20 or len(title) > 70:
            issues.append({"category": "SEO", "severity": "MEDIUM", "message": f"Title length ({len(title)} chars) should be between 30 and 60 chars."})
            score -= 5

        meta_desc = parser.meta.get("description", "")
        if not meta_desc:
            issues.append({"category": "SEO", "severity": "HIGH", "message": "Missing meta description."})
            score -= 15
        elif len(meta_desc) < 50 or len(meta_desc) > 160:
            issues.append({"category": "SEO", "severity": "LOW", "message": f"Meta description length ({len(meta_desc)} chars) recommended between 50 and 160 chars."})
            score -= 5

        if parser.h1_count == 0:
            issues.append({"category": "SEO", "severity": "HIGH", "message": "Missing <h1> heading."})
            score -= 10
        elif parser.h1_count > 1:
            issues.append({"category": "SEO", "severity": "MEDIUM", "message": f"Multiple ({parser.h1_count}) <h1> tags found. Recommend single top-level heading."})
            score -= 5

        # Accessibility Checks
        if parser.images_missing_alt > 0:
            issues.append({"category": "Accessibility", "severity": "HIGH", "message": f"{parser.images_missing_alt} out of {parser.images_total} images missing alt text."})
            score -= min(15, parser.images_missing_alt * 3)

        if not parser.viewport_present:
            issues.append({"category": "Mobile/Responsive", "severity": "HIGH", "message": "Missing viewport meta tag for mobile responsiveness."})
            score -= 15

        # Security Headers Checks
        sec_headers = {
            "strict-transport-security": "HSTS header missing",
            "x-content-type-options": "X-Content-Type-Options header missing",
            "x-frame-options": "X-Frame-Options (Clickjacking protection) missing",
            "content-security-policy": "Content-Security-Policy (CSP) missing"
        }
        lower_headers = {k.lower(): v for k, v in headers.items()}
        for h_key, h_msg in sec_headers.items():
            if h_key not in lower_headers:
                issues.append({"category": "Security", "severity": "MEDIUM", "message": h_msg})
                score -= 5

        # Performance Check
        if latency_ms > 1500:
            issues.append({"category": "Performance", "severity": "MEDIUM", "message": f"High response latency: {latency_ms}ms"})
            score -= 10

        score = max(0, score)

        return {
            "success": True,
            "url": url,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "overall_score": score,
            "metrics": {
                "title": title,
                "meta_description": meta_desc,
                "h1_count": parser.h1_count,
                "h2_count": parser.h2_count,
                "images_total": parser.images_total,
                "images_missing_alt": parser.images_missing_alt,
                "canonical_url": parser.canonical_url or None,
                "internal_links": parser.internal_links,
                "external_links": parser.external_links,
                "html_size_kb": round(len(content_bytes) / 1024, 2)
            },
            "issues_count": len(issues),
            "issues": issues
        }

    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}
