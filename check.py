async def check_verification(bot, event, user_tokens_collection):
    user_id = event.sender_id

    # Check if the user is a premium user
    user = await user_tokens_collection.find_one({"user_id": user_id, "is_premium": True})

    if user:
        await event.reply("𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐧𝐞𝐞𝐝 𝐚𝐧𝐲 𝐯𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧")
        return

    # Check if the user is verified in the MongoDB collection
    user = await user_tokens_collection.find_one({"user_id": user_id, "verified": True})

    if user:
        await event.reply("𝐘𝐨𝐮 𝐚𝐫𝐞 𝐯𝐞𝐫𝐢𝐟𝐢𝐞𝐝.")
    else:
        await event.reply("𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐯𝐞𝐫𝐢𝐟𝐢𝐞𝐝.")
