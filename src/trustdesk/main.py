import logging
from fastapi import FastAPI, Request

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
    log.info("webhook received: %s", payload)
    return {"ok": True}
