import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from app.config import settings


class SlackAPIError(Exception):
    """Raised when Slack returns a 5xx response to trigger a retry."""

    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body
        super().__init__(f"Slack returned {status_code}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException, SlackAPIError)),
    reraise=True,
)
async def send_to_slack(formatted_data: str) -> tuple[int, dict]:
    payload = {"text": formatted_data}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10.0,
        )

    try:
        response_body = response.json()
    except Exception:
        response_body = {"raw": response.text}

    if response.status_code >= 500:
        raise SlackAPIError(response.status_code, response_body)

    return response.status_code, response_body
