import hashlib
import hmac

import httpx

from trustdesk.channels.base import InboundMessage
from trustdesk.config import settings

CHANNEL = "meta"


def verify_signature(raw_body: bytes, header: str | None) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(settings.meta_app_secret.get_secret_value(
    ).encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def parse_meta(payload: dict) -> list[InboundMessage]:
    out: list[InboundMessage] = []
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for m in value.get("messages") or []:
                if m.get("type") != "text":
                    continue
                text = (m.get("text") or {}).get("body")
                msg_id, sender = m.get("id"), m.get("from")
                if not (text and msg_id and sender):
                    continue
                out.append(InboundMessage(channel=CHANNEL, message_id=msg_id,
                           contact_id=sender, text=text, from_me=False, is_group=False))
    return out


async def send_text(client: httpx.AsyncClient, to: str, text: str) -> None:
    url = (f"https://graph.facebook.com/{settings.meta_api_version}/"
           f"{settings.meta_phone_number_id}/messages")
    response = await client.post(
        url,
        headers={
            "Authorization": f"Bearer {settings.meta_access_token.get_secret_value()}"},
        json={"messaging_product": "whatsapp",
              "to": to, "text": {"body": text}},
        timeout=10.0,
    )

    response.raise_for_status()
