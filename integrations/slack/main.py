"""
community_hub/integrations/slack/main.py
Slack workspace connector for webhook alerts and Bot API messages.
"""

import os
import urllib.request
import json
from typing import Dict, Any, Optional


class SlackConnector:
    def __init__(self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")

    def post_webhook(self, text: str, blocks: Optional[list] = None) -> Dict[str, Any]:
        """Send message via Incoming Webhook URL."""
        if not self.webhook_url:
            return {"success": False, "error": "Missing SLACK_WEBHOOK_URL."}

        payload: Dict[str, Any] = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=body,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"success": True, "status_code": resp.getcode(), "response": resp.read().decode("utf-8")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_message(self, channel: str, text: str) -> Dict[str, Any]:
        """Post message to channel using Bot Token."""
        if not self.bot_token:
            return {"success": False, "error": "Missing SLACK_BOT_TOKEN."}

        url = "https://slack.com/api/chat.postMessage"
        payload = {"channel": channel, "text": text}
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"success": data.get("ok", False), "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main(action: str = "post_webhook", **kwargs) -> Dict[str, Any]:
    connector = SlackConnector()
    if hasattr(connector, action):
        func = getattr(connector, action)
        return func(**kwargs)
    return {"success": False, "error": f"Unknown Slack action '{action}'"}
