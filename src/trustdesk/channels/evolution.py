from .base import InboundMessage

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
