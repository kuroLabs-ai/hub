"""
community_hub/integrations/discord/main.py
Discord Webhook connector for dispatching operational alerts, rich embeds, and build notifications.
"""

import os
import urllib.request
import json
from typing import Dict, Any, List, Optional


class DiscordConnector:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")

    def send_message(self, content: str, username: str = "KuroCode Hub Alert") -> Dict[str, Any]:
        """Send plain text message to Discord channel via webhook."""
        if not self.webhook_url:
            return {"success": False, "error": "Missing DISCORD_WEBHOOK_URL environment variable."}

        payload = {
            "content": content,
            "username": username
        }

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "KuroCode-Discord-Connector/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {
                    "success": True,
                    "status_code": resp.getcode(),
                    "message": "Notification dispatched successfully"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x5865F2,  # Discord Blurple
        fields: Optional[List[Dict[str, Any]]] = None,
        username: str = "KuroCode Hub Alert"
    ) -> Dict[str, Any]:
        """Send rich embed card to Discord."""
        if not self.webhook_url:
            return {"success": False, "error": "Missing DISCORD_WEBHOOK_URL environment variable."}

        embed: Dict[str, Any] = {
            "title": title,
            "description": description,
            "color": color
        }
        if fields:
            embed["fields"] = fields

        payload = {
            "username": username,
            "embeds": [embed]
        }

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "KuroCode-Discord-Connector/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {
                    "success": True,
                    "status_code": resp.getcode(),
                    "message": "Embed dispatched successfully"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


def main(action: str = "send_message", **kwargs) -> Dict[str, Any]:
    connector = DiscordConnector()
    if hasattr(connector, action):
        func = getattr(connector, action)
        return func(**kwargs)
    return {"success": False, "error": f"Unknown Discord action '{action}'"}
