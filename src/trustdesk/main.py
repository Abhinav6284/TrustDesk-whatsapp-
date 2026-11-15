import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import PlainTextResponse

from trustdesk.channels import meta
from trustdesk.channels.base import InboundMessage
from trustdesk.channels.evolution import parse_evolution, send_text
from trustdesk.config import settings

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("trustdesk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient()
    yield
    await app.state.http.aclose()


app = FastAPI(title="TrustDesk", lifespan=lifespan)


async def reply(client: httpx.AsyncClient, msg: InboundMessage) -> None:
    try:
        await send_text(client, msg.contact_id, f"echo: {msg.text}")
        log.info("replied to %s", msg.contact_id)
    except httpx.HTTPError as e:
        log.error("send failed to %s: %r", msg.contact_id, e)


def _allowed(number: str) -> bool:
    allowed = {n.strip()
               for n in settings.meta_allowed_numbers.split(",") if n.strip()}
    return not allowed or number in allowed


async def meta_reply(client: httpx.AsyncClient, msg: InboundMessage) -> None:
    try:
        await meta.send_text(client, msg.contact_id, f"echo: {msg.text}")
        log.info("meta replied to %s", msg.contact_id)
    except httpx.HTTPStatusError as e:
        log.error("meta send failed %s: %s",
                  e.response.status_code, e.response.text)
    except httpx.HTTPError as e:
        log.error("meta send failed: %r", e)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/webhooks/evolution")
async def evolution_webhook(request: Request, background: BackgroundTasks) -> dict:
    payload = await request.json()
    msg = parse_evolution(payload)

    if msg is None:
        log.info("ignored: not a text message (event=%s)", payload.get("event"))
        return {"ok": True}
    if msg.from_me or msg.is_group:
        log.info("ignored: from_me=%s is_group=%s", msg.from_me, msg.is_group)
        return {"ok": True}

    log.info("message from %s: %s", msg.contact_id, msg.text)
    background.add_task(reply, request.app.state.http, msg)
    return {"ok": True}


@app.get("/webhooks/meta")
async def meta_verify(request: Request):
    params = request.query_params
    if (params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == settings.meta_verify_token.get_secret_value()):
        log.info("meta webhook verified")
        return PlainTextResponse(params.get("hub.challenge", ""))
    log.warning("meta verify failed")
    return PlainTextResponse("forbidden", status_code=403)


@app.post("/webhooks/meta")
async def meta_webhook(request: Request, background: BackgroundTasks):
    raw = await request.body()
    if not meta.verify_signature(raw, request.headers.get("X-Hub-Signature-256")):
        log.warning("meta: bad signature")
        return PlainTextResponse("forbidden", status_code=403)

    msgs = meta.parse_meta(await request.json())
    if not msgs:
        log.info("meta: no text messages (statuses or other)")
        return {"ok": True}

    for msg in msgs:
        if not _allowed(msg.contact_id):
            log.info("meta: ignored, not in allowlist")
            continue
        log.info("meta message from %s: %s", msg.contact_id, msg.text)
        background.add_task(meta_reply, request.app.state.http, msg)
    return {"ok": True}
