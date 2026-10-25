from .base import InboundMessage
import httpx
from trustdesk.config import settings


CHANNEL = "evolution"
MESSAGE_EVENTS = {"messages.upsert", "MESSAGES_UPSERT"}


def _extract_text(message: dict) -> str | None:
    if text := message.get("conversation"):
        return text
    extended = message.get("extendedTextMessage") or {}
    return extended.get("text")


def parse_evolution(payload: dict) -> InboundMessage | None:
    if payload.get("event") not in MESSAGE_EVENTS:
        return None

    data = payload.get("data") or {}
    key = data.get("key") or {}
    message = data.get("message") or {}

    text = _extract_text(message)
    message_id = key.get("id")
    contact_id = key.get("remoteJid")
    if not (text and message_id and contact_id):
        return None

    return InboundMessage(
        channel=CHANNEL,
        message_id=message_id,
        contact_id=contact_id,
        text=text,
        from_me=bool(key.get("fromMe", False)),
        is_group=contact_id.endswith("@g.us")
    )


async def send_text(client: httpx.AsyncClient,
                    contact_id: str, text: str) -> None:
    number = contact_id.split("@")[0]
    url = f"{settings.evolution_url}/message/sendText/{settings.evolution_instance}"
    response = await client.post(
        url,
        headers={"apikey": settings.evolution_api_key.get_secret_value()},
        json={"number": number, "text": text},
        timeout=10.0,

    )
    response.raise_for_status()