import logging
from fastapi import FastAPI, Request, BackgroundTasks, background
from .channels.evolution import parse_evolution
from contextlib import asynccontextmanager

import httpx

from trustdesk.channels.base import InboundMessage
from trustdesk.channels.evolution import parse_evolution, send_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
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
