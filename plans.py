from motor.motor_asyncio import AsyncIOMotorClient
from config import *

async def plans_command(m):
    user_id = m.sender_id
    user = await m.client.get_entity(user_id)

    # Connect to MongoDB using motor
    client = AsyncIOMotorClient(MONGO_DB_URL)
    db = client[DB_NAME]
    user_tokens_collection = db["user_tokens"]

    # Check if the user is premium
    user_data = await user_tokens_collection.find_one({"user_id": user_id})
    is_premium = user_data.get("is_premium", False) if user_data else False

    if is_premium:
        # Premium user
        reply_text = f"𝘠𝘰𝘶 𝘢𝘳𝘦 𝘢𝘭𝘳𝘦𝘢𝘥𝘺 𝘢 𝘱𝘳𝘦𝘮𝘪𝘶𝘮 𝘶𝘴𝘦𝘳, {user.first_name}! 🌟"
    else:
        # Free user
        full_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
        reply_text = f"""
𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}

𝐍𝐚𝐦𝐞: {full_name}

💠 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐏𝐚𝐜𝐤𝐚𝐠𝐞: 💠

  ✓ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐮𝐩𝐭𝐨 𝟐.𝟎 𝐆𝐁
  ✓ 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐓𝐚𝐬𝐤𝐬
  ✓ 𝐍𝐨 𝐓𝐢𝐦𝐞 𝐑𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬
  ✓ 𝐍𝐨 𝐀𝐧𝐭𝐢-𝐒𝐩𝐚𝐦 𝐓𝐢𝐦𝐞𝐫
  ✓ 𝐕𝐚𝐥𝐢𝐝𝐢𝐭𝐲: 𝟏 𝐌𝐎𝐍𝐓𝐇

   𝐏𝐫𝐢𝐜𝐞: 𝟔𝟎 𝐈𝐍𝐑 ₹

𝐆𝐞𝐭 𝐢𝐭 𝐧𝐨𝐰 𝐟𝐫𝐨𝐦: @{ADMIN_USERNAME}
"""

    await m.reply(reply_text, parse_mode="markdown")
