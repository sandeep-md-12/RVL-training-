import asyncio
import redis.asyncio as aioredis

async def test_connection():
    try:
        redis_client = aioredis.from_url("redis://127.0.0.1:6379", decode_responses=True)
        print("Writing data to Redis...")
        await redis_client.set("my_learning_key", "Redis is working with Python!")
        print("Reading data back from Redis...")
        value = await redis_client.get("my_learning_key")
        print(f"\n✅ SUCCESS! Python successfully connected to Redis.")
        print(f"Fetched value: '{value}'\n")
        await redis_client.delete("my_learning_key")
        await redis_client.close()
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED.")
        print(f"Error details: {e}\n")

asyncio.run(test_connection())
