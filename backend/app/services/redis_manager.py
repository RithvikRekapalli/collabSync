import redis.asyncio as redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

async def publish(channel: str, message: str):
    await redis_client.publish(channel, message)

async def subscribe(channel: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    return pubsub
