import asyncio

async def broadcast_message(bot, event, OWNER_ID, user_tokens_collection):
    # Check if the user is an admin
    if event.sender_id in OWNER_ID:
        message = event.pattern_match.group(1)

        # Fetch user tokens from MongoDB
        user_tokens = await load_user_tokens(user_tokens_collection)

        # Iterate through user tokens and send the message to all users
        for user in user_tokens:
            try:
                # Check if the user is not an admin
                if user['user_id'] not in OWNER_ID:
                    await bot.send_message(user['user_id'], message)
            except Exception as e:
                print(f"Error sending message to user {user['user_id']}: {e}")

        await event.reply("𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐚𝐥𝐥 𝐮𝐬𝐞𝐫𝐬.")
    else:
        await event.reply("𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.")

# Function to load user tokens from MongoDB
async def load_user_tokens(user_tokens_collection):
    user_tokens = []
    async for user in user_tokens_collection.find():
        user_tokens.append(user)
    return user_tokens
