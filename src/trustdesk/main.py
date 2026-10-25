import logging
from fastapi import FastAPI, Request
from .channels.evolution import parse_evolution



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("trustdesk")

app = FastAPI(title="TrustDesk")


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/webhooks/evolution")
async def evolution_webhook(request: Request) -> dict:
    payload = await request.json()

    msg = parse_evolution(payload)

    if msg is None:
        log.info("ignored: not a text message (event=%s)", payload.get("event"))
        return {"ok": True}

    if msg.from_me or msg.is_group:
        log.info("ignored: from_me=%s is_group=%s", msg.from_me, msg.is_group)
        return {"ok": True}

    log.info("message from %s: %s", msg.contact_id, msg.text)
    return {"ok": True}


    




    

    