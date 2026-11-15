import hashlib
import hmac

from trustdesk.channels.meta import parse_meta, verify_signature


def sign(body: bytes, secret: str = "test-secret") -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def make_payload(messages=None, statuses=None):
    value = {}
    if messages is not None:
        value["messages"] = messages
    if statuses is not None:
        value["statuses"] = statuses
    return {"entry": [{"changes": [{"field": "messages", "value": value}]}]}


def text_msg(body="hi", msg_id="wamid.1", sender="919876543210"):
    return {"from": sender, "id": msg_id, "type": "text", "text": {"body": body}}


def test_valid_signature():
    body = b'{"a": 1}'
    assert verify_signature(body, sign(body)) is True


def test_wrong_secret_rejected():
    body = b'{"a": 1}'
    assert verify_signature(body, sign(body, "attacker")) is False


def test_tampered_body_rejected():
    assert verify_signature(b'{"a": 2}', sign(b'{"a": 1}')) is False


def test_missing_or_malformed_header_rejected():
    assert verify_signature(b"x", None) is False
    assert verify_signature(b"x", "md5=abc") is False


def test_parse_text_message():
    msgs = parse_meta(make_payload([text_msg()]))
    assert len(msgs) == 1
    m = msgs[0]
    assert (m.channel, m.text, m.message_id, m.contact_id) == (
        "meta", "hi", "wamid.1", "919876543210")


def test_parse_multiple_messages():
    msgs = parse_meta(make_payload(
        [text_msg(msg_id="a"), text_msg(msg_id="b")]))
    assert [m.message_id for m in msgs] == ["a", "b"]


def test_status_update_ignored():
    assert parse_meta(make_payload(statuses=[{"status": "delivered"}])) == []


def test_non_text_ignored():
    assert parse_meta(make_payload(
        [{"from": "91", "id": "x", "type": "image"}])) == []


def test_garbage_ignored():
    assert parse_meta({}) == []
