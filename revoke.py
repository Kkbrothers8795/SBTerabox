from random import choices
from string import ascii_uppercase, digits
from motor.motor_asyncio import AsyncIOMotorClient
from config import *

mongo_client = AsyncIOMotorClient(MONGO_DB_URL)
db = mongo_client[DB_NAME]  # Specify the database name
user_tokens_collection = db["user_tokens"]

async def revoke_tokens(bot):
    # Get all user tokens from the MongoDB collection
    user_tokens = await load_user_tokens()

    # Generate new tokens for each user and update their verification status
    for user in user_tokens:
        new_token = ''.join(choices(ascii_uppercase + digits, k=15))

        # Update the user's token and verification status in the MongoDB collection
        await user_tokens_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"token": new_token, "verified": False}}
        )

    return "𝐀𝐥𝐥 𝐮𝐬𝐞𝐫 𝐭𝐨𝐤𝐞𝐧𝐬 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐫𝐞𝐯𝐨𝐤𝐞𝐝"

async def load_user_tokens():
    user_tokens = []
    async for user in user_tokens_collection.find():
        user_tokens.append(user)
    return user_tokens

async def send_reset_message(bot):
    # Get all user tokens from the MongoDB collection
    user_tokens = await load_user_tokens()

    # Send a message to non-admin users
    for user in user_tokens:
        if user["user_id"] not in OWNER_ID:  # Skip sending message to admins
            try:
                await bot.send_message(user["user_id"], "【｡_｡】 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭𝐞𝐝 & 𝐓𝐨𝐤𝐞𝐧'𝐬 𝐚𝐫𝐞 𝐑𝐞𝐯𝐨𝐤𝐞𝐝 【｡_｡】")
            except Exception as e:
                print(f"Failed to send message to user {user['user_id']}: {e}")

    return "Bot Reset messages sent to non-admin users."

