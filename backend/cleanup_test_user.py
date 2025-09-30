import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def cleanup():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db = client[os.getenv("DB_NAME")]
    result = await db.users.delete_many({"username": "testuser123"})
    print(f"Deleted {result.deleted_count} test users")
    client.close()

asyncio.run(cleanup())