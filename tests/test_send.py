import json

import httpx
import pytest

from trustdesk.channels.evolution import send_text


async def test_send_text_builds_correct_request():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["req"] = request
        return httpx.Response(200, json={"ok": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await send_text(client, "919876543210@s.whatsapp.net", "hello")

    req = captured["req"]
    assert req.method == "POST"
    assert str(req.url) == "http://evolution.test/message/sendText/trustdesk"
    assert req.headers["apikey"] == "test-key"
    assert json.loads(req.content) == {
        "number": "919876543210", "text": "hello"}


async def test_send_text_raises_on_server_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await send_text(client, "919876543210@s.whatsapp.net", "hello")
