import logging
import time

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def notify_order_placed(user: dict, order_id: int, total: int) -> None:
    if not settings.webhook_url:
        return

    payload = {
        "event": "order.placed",
        "order_id": order_id,
        "total": total,
        "customer": {"name": user["name"], "email": user["email"]},
    }
    headers = {"Authorization": f"Bearer {settings.webhook_token}"}
    logger.info("send webhook: headers=%s payload=%s", headers, payload)

    for attempt in range(MAX_RETRIES):
        try:
            res = httpx.post(settings.webhook_url, json=payload, headers=headers, timeout=3)
            res.raise_for_status()
            return
        except httpx.HTTPError:
            logger.warning("webhook failed (attempt %d)", attempt + 1)
            time.sleep(2**attempt)
    logger.error("webhook gave up: order_id=%s", order_id)
