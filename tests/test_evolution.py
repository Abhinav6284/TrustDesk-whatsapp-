from trustdesk.channels.evolution import parse_evolution


def payload(message, jid="919876543210@s.whatsapp.net", from_me=False,
            event="messages.upsert", msg_id="ID1"):
    return {
        "event": event,
        "data": {
            "key": {"remoteJid": jid, "fromMe": from_me, "id": msg_id},
            "message": message,
        }
    }


def taste_plain_text():
    m = parse_evolution(payload({"conversation": "hi"}))
    assert m is not None
    assert m.text == "hi"
    assert m.message_id == "ID1"
    assert m.contact_id == "919876543210@s.whatsapp.net"
    assert m.channel == "evolution"


def test_extended_text():
    m = parse_evolution(payload({"extendedTextMessage": {"text": "yo"}}))
    assert m.text == "yo"


def test_from_me_flag():
    assert parse_evolution(
        payload({"conversation": "hi"}, from_me=True)).from_me is True


def test_group_flag():
    assert parse_evolution(
        payload({"conversation": "hi"}, jid="919876543210@g.us")).is_group is True


def test_other_event_ignored():
    assert parse_evolution(
        payload({"conversation": "hi"}, event="connection.update")) is None


def test_image_ignored():
    assert parse_evolution(payload({"imageMessage": {"url": " "}})) is None


def test_garbage_ignored():
    assert parse_evolution({}) is None
    assert parse_evolution({"event": "messages.upsert"}) is None
