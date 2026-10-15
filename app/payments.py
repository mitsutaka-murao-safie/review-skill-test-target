import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RefundError(Exception):
    pass


def refund(order_id: int, amount: int) -> None:
    try:
        res = httpx.post(
            f"{settings.payment_api_url}/refunds",
            json={"order_id": order_id, "amount": amount},
            timeout=5,
        )
        res.raise_for_status()
    except httpx.HTTPError as e:
        logger.exception("refund request failed: order_id=%s", order_id)
        raise RefundError(str(e)) from e
