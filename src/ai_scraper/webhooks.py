"""Webhook notification support."""

import asyncio
import json
from dataclasses import dataclass
from typing import Optional

import aiohttp


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    url: str
    events: list[str]  # ["scrape_complete", "trending_found", "error"]
    headers: Optional[dict] = None


class WebhookNotifier:
    """Send webhook notifications."""

    def __init__(self, webhooks: list[WebhookConfig]):
        self.webhooks = webhooks
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def notify(self, event: str, data: dict) -> None:
        """Send notification for an event.

        Args:
            event: Event name.
            data: Event data.
        """
        session = await self._get_session()

        payload = {
            "event": event,
            "timestamp": data.get("timestamp"),
            "data": data,
        }

        for webhook in self.webhooks:
            if event not in webhook.events:
                continue

            try:
                async with session.post(
                    webhook.url,
                    json=payload,
                    headers=webhook.headers,
                ) as response:
                    if response.status >= 400:
                        print(f"Webhook failed: {response.status}")
            except Exception as e:
                print(f"Webhook error: {e}")

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()


# Built-in formatters for common services
def format_slack_message(event: str, data: dict) -> dict:
    """Format message for Slack webhook."""
    if event == "scrape_complete":
        return {
            "text": "Scrape Complete",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Scrape Complete*\n"
                                f"Found {data.get('repos_count', 0)} AI repositories\n"
                                f"Total stars: {data.get('total_stars', 0):,}",
                    },
                }
            ],
        }
    return {"text": f"Event: {event}"}


def format_telegram_message(event: str, data: dict) -> str:
    """Format message for Telegram bot."""
    if event == "scrape_complete":
        return (
            f"🤖 *Scrape Complete*\n\n"
            f"📊 Found {data.get('repos_count', 0)} AI repositories\n"
            f"⭐ Total stars: {data.get('total_stars', 0):,}"
        )
    return f"Event: {event}"
