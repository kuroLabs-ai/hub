"""
community_hub/tools/web_scraper.py
Extract structured information (title, metadata, headings, text, links) from permitted webpages.
"""

from typing import Dict, Any, List
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser


class SimpleHTMLDataExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: str = ""
        self.in_title: bool = False
        self.meta: Dict[str, str] = {}
        self.headings: List[Dict[str, str]] = []
        self.current_heading_tag: str = ""
        self.current_heading_text: List[str] = []
        self.links: List[Dict[str, str]] = []
        self.text_chunks: List[str] = []
        self.ignore_tags = {"script", "style", "noscript", "svg"}
        self.current_ignore: int = 0

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        if tag_lower in self.ignore_tags:
            self.current_ignore += 1
            return

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta":
            name = attr_dict.get("name") or attr_dict.get("property")
            content = attr_dict.get("content")
            if name and content:
                self.meta[name] = content
        elif tag_lower in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.current_heading_tag = tag_lower
            self.current_heading_text = []
        elif tag_lower == "a":
            href = attr_dict.get("href")
            if href:
                self.links.append({"href": href, "text": ""})

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in self.ignore_tags:
            if self.current_ignore > 0:
                self.current_ignore -= 1
            return

        if tag_lower == "title":
            self.in_title = False
        elif tag_lower in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self.current_heading_tag:
                text = " ".join("".join(self.current_heading_text).split())
                if text:
                    self.headings.append({"level": self.current_heading_tag, "text": text})
                self.current_heading_tag = ""
                self.current_heading_text = []

    def handle_data(self, data: str):
        if self.current_ignore > 0:
            return

        text = data.strip()
        if not text:
            return

        if self.in_title:
            self.title = (self.title + " " + text).strip()
        elif self.current_heading_tag:
            self.current_heading_text.append(data)
        else:
            self.text_chunks.append(text)

        if self.links and not self.links[-1]["text"]:
            self.links[-1]["text"] = text


def web_scraper(url: str, max_text_chars: int = 5000, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch and parse a webpage to extract title, metadata, headings, text summary, and links.
    
    Args:
        url: The web URL to scrape.
        max_text_chars: Maximum characters of readable body text to return.
        timeout: Network request timeout in seconds.
    """
    if not url.startswith(("http://", "https://")):
        return {"success": False, "error": "URL must begin with http:// or https://"}

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KuroCode-WebScraper/1.0"
            }
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            content_type = response.headers.get_content_type()
            
            if "html" not in content_type:
                return {
                    "success": False,
                    "error": f"Unsupported Content-Type '{content_type}'. web_scraper handles HTML pages."
                }

            html_bytes = response.read(1_000_000)  # Max 1MB
            encoding = response.headers.get_content_charset() or "utf-8"
            html_text = html_bytes.decode(encoding, errors="replace")

        parser = SimpleHTMLDataExtractor()
        parser.feed(html_text)

        body_text = " ".join(parser.text_chunks)
        if len(body_text) > max_text_chars:
            body_text = body_text[:max_text_chars] + "... [truncated]"

        # Format links with resolved absolute URL if possible
        formatted_links = []
        for item in parser.links[:50]:
            resolved = urllib.parse.urljoin(url, item["href"])
            formatted_links.append({"url": resolved, "text": item["text"]})

        return {
            "success": True,
            "url": url,
            "status_code": status_code,
            "title": parser.title,
            "meta": parser.meta,
            "headings": parser.headings[:30],
            "links_count": len(parser.links),
            "links": formatted_links,
            "text": body_text
        }

    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}
