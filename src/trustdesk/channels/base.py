from dataclasses import dataclass

@dataclass(frozen=True)
class InboundMessage:
    channel: str
    message_id: str
    contact_id: str
    text: str
    from_me: bool
    is_group: bool


