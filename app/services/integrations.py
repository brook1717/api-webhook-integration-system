import httpx

from app.config import settings


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

    return response.status_code, response_body
