from fakeredis import FakeAsyncRedis
from redis.exceptions import ConnectionError as RedisConnectionError

from trustdesk.channels.base import InboundMessage
from trustdesk.dedupe import TTL_SECONDS, is_new


def make_msg(msg_id="ID1", channel="meta"):
    return InboundMessage(channel=channel, message_id=msg_id, contact_id="919876543210",
                          text="hi", from_me=False, is_group=False)


async def test_first_is_new_second_is_duplicate():
    r = FakeAsyncRedis()
    assert await is_new(r, make_msg()) is True
    assert await is_new(r, make_msg()) is False


async def test_different_ids_are_independent():
    r = FakeAsyncRedis()
    assert await is_new(r, make_msg("A")) is True
    assert await is_new(r, make_msg("B")) is True


async def test_same_id_on_different_channels_is_independent():
    r = FakeAsyncRedis()
    assert await is_new(r, make_msg("X", "meta")) is True
    assert await is_new(r, make_msg("X", "evolution")) is True


async def test_key_expires():
    r = FakeAsyncRedis()
    await is_new(r, make_msg())
    ttl = await r.ttl("dedupe:meta:ID1")
    assert 0 < ttl <= TTL_SECONDS


class BrokenRedis:
    async def set(self, *args, **kwargs):
        raise RedisConnectionError("down")


async def test_fails_open_when_redis_down():
    assert await is_new(BrokenRedis(), make_msg()) is True
