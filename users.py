async def users_command(bot, event, OWNER_ID, user_tokens_collection):
    # Check if the sender is an admin
    if event.sender_id not in OWNER_ID:
        return await event.reply("𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.")

    # Fetch user tokens from MongoDB
    user_tokens = await load_user_tokens(user_tokens_collection)

    # Get the count of unique user IDs
    unique_users = len(set(user['user_id'] for user in user_tokens))

    # Send the count of users as a reply
    await event.reply(f"𝐓𝐨𝐭𝐚𝐥 𝐮𝐬𝐞𝐫𝐬 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭: {unique_users}")

# Function to load user tokens from MongoDB
async def load_user_tokens(user_tokens_collection):
    user_tokens = []
    async for user in user_tokens_collection.find():
        user_tokens.append(user)
    return user_tokens
