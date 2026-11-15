import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from trustdesk.channels.base import InboundMessage

log = logging.getLogger("trustdesk.dedupe")

TTL_SECONDS = 24 * 60 * 60


async def is_new(redis: Redis, msg: InboundMessage) -> bool:
    key = f"dedupe:{msg.channel}:{msg.message_id}"
    try:
        created = await redis.set(key, 1, nx=True, ex=TTL_SECONDS)
    except RedisError as e:
        log.warning("redis unavailable, skipping dedupe check: %r", e)
        return True
    return bool(created)
