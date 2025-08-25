import asyncio
from random import choices
from string import ascii_uppercase, digits
import os
import time
from uuid import uuid4
import requests
from revoke import revoke_tokens, send_reset_message
import datetime

import telethon
import redis
from telethon import TelegramClient, events, Button
from telethon.tl import functions
from telethon.types import Message, UpdateNewMessage
from telethon.tl.functions.messages import ForwardMessagesRequest
from motor.motor_asyncio import AsyncIOMotorClient  # Import AsyncIOMotorClient
from broadcast import broadcast_message
from users import users_command
from check import check_verification

from plans import plans_command  # Import the new feature file
from cansend import CanSend
from config import *
from terabox import get_data
from tools import (
    convert_seconds,
    download_file,
    download_image_to_bytesio,
    extract_code_from_url,
    get_formatted_size,
    get_urls_from_string,
    is_user_on_chat,
)

bot = TelegramClient("tele", API_ID, API_HASH)

# Connect to MongoDB using AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(MONGO_DB_URL)
db = mongo_client[DB_NAME]  # Specify the database name

# Define MongoDB collections
user_tokens_collection = db["user_tokens"]

db = redis.Redis(
    host=HOST,
    port=PORT,
    password=PASSWORD,
    decode_responses=True,
)

@bot.on(events.NewMessage(pattern=r'/start (.+)', incoming=True, outgoing=False))
async def start(event):
    token_to_check = event.pattern_match.group(1)

    # Check if the token exists in the MongoDB collection
    user = await user_tokens_collection.find_one({"token": token_to_check})

    if user:
        # Update the user's verified status and add timestamp
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await user_tokens_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"verified": True, "verified_at": current_time}}
        )
        await event.reply("𝐃𝐞𝐚𝐫 𝐔𝐬𝐞𝐫\n\n𝐘𝐨𝐮 𝐚𝐫𝐞 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐯𝐞𝐫𝐢𝐟𝐢𝐞𝐝!\n\n𝐅𝐨𝐫 𝟐𝟒 𝐇𝐨𝐮𝐫𝐬 𝐄𝐧𝐣𝐨𝐲 ❤️")
    elif token_to_check.isupper():  # Check if the token is in uppercase
        await event.reply(f"𝐢𝐧𝐯𝐚𝐥𝐢𝐝 𝐭𝐨𝐤𝐞𝐧. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.\n\n𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐨 𝐀𝐝𝐦𝐢𝐧 @{ADMIN_USERNAME}")

@bot.on(events.NewMessage(pattern="/start$", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    user_id = m.sender_id

    # Check if the user exists in the MongoDB collection
    user = await user_tokens_collection.find_one({"user_id": user_id})

    if not user:
        # Generate a random 15-character token in uppercase letters
        token = ''.join(choices(ascii_uppercase + digits, k=15))

        # Add the new user to the MongoDB collection
        await user_tokens_collection.insert_one({"user_id": user_id, "token": token, "verified": False, "is_premium": False})

    image_url = START_IMAGE
    reply_text = """
    𝐇𝐞𝐥𝐥𝐨! 𝐈 𝐚𝐦 𝐓𝐞𝐫𝐚𝐛𝐨𝐱 𝐕𝐢𝐝𝐞𝐨 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭.
𝐒𝐞𝐧𝐝 𝐦𝐞 𝐭𝐞𝐫𝐚𝐛𝐨𝐱 𝐯𝐢𝐝𝐞𝐨 𝐥𝐢𝐧𝐤 & 𝐈 𝐰𝐢𝐥𝐥 𝐬𝐞𝐧𝐝 𝐕𝐢𝐝𝐞𝐨.

𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 : /plans"""

    msg_text = "𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐛𝐞𝐟𝐨𝐫𝐞 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭."
    btn_txt = "⚠️ 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 ⚠️"
    channel_username = f"https://t.me/{CHANNEL_USERNAME}"
    button = Button.url(btn_txt, channel_username)

    channel = CHANNEL_USERNAME
    if not await is_user_on_chat(bot, channel, m.peer_id):
        return await m.reply(msg_text, buttons=button)

    await m.reply(reply_text, file=image_url, link_preview=False, parse_mode="markdown")


    
@bot.on(events.NewMessage(pattern="/start (.*)", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    text = m.pattern_match.group(1)
    fileid = db.get(str(text))

    channel1 = CHANNEL_USERNAME

    check_channel1 = await is_user_on_chat(bot, channel1, m.peer_id)

    if not check_channel1:
        return await m.reply(f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 {channel1} 𝐛𝐞𝐟𝐨𝐫𝐞 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭.")
    
    if fileid is not None:
       await bot(
        ForwardMessagesRequest(
            from_peer=PRIVATE_CHAT_ID,
            id=[int(fileid)],
            to_peer=m.chat.id,
            drop_author=True,
            noforwards=False,
            background=True,
            drop_media_captions=False,
            with_my_score=True,
        )
    )

@bot.on(events.NewMessage(pattern="/check$", incoming=True, outgoing=False))
async def check_handler(event):
    await check_verification(bot, event, user_tokens_collection)
        
# Add the new feature to the bot
@bot.on(events.NewMessage(pattern="/plans$", incoming=True, outgoing=False))
async def plans_command_wrapper(event):
    await plans_command(event)

@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text
        and get_urls_from_string(message.text)
        and message.is_private,
    )
)
async def get_message(m: Message):
    asyncio.create_task(handle_message(m))

@bot.on(events.NewMessage(pattern="/users$", incoming=True, outgoing=False))
async def users_handler(event):
    await users_command(bot, event, OWNER_ID, user_tokens_collection)
    
@bot.on(events.NewMessage(pattern="/broadcast (.+)", incoming=True, outgoing=False))
async def broadcast_handler(event):
    await broadcast_message(bot, event, OWNER_ID, user_tokens_collection)

@bot.on(events.NewMessage(pattern="/revoke$", incoming=True, outgoing=False))
async def revoke_handler(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("You are not authorized to use this command.")

    result = await revoke_tokens(bot)
    await event.reply(result)

    # Send "Bot Reset" message to non-admin users
    reset_result = await send_reset_message(bot)
    print(reset_result)  # Print the result to the console

@bot.on(events.NewMessage(pattern=r"/pro (\d+)(?:\s+-r)?$", incoming=True, outgoing=False))
async def set_premium(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("You are not authorized to use this command.")

    user_id_to_premium = int(event.pattern_match.group(1))
    is_remove = "-r" in event.raw_text

    # Query the database to check the current premium status of the user
    user_data = await user_tokens_collection.find_one({"user_id": user_id_to_premium})
    if user_data:
        current_premium_status = user_data.get("is_premium", False)
    else:
        return await event.reply(f"User with ID {user_id_to_premium} not found.")

    # If the user is already a premium user and -r flag is not present, no need to update
    if current_premium_status and not is_remove:
        return await event.reply(f"User with ID {user_id_to_premium} is already a premium user.")

    # Update the user's premium status based on whether -r flag is provided
    new_premium_status = not is_remove

    result = await user_tokens_collection.update_one(
        {"user_id": user_id_to_premium},
        {"$set": {"is_premium": new_premium_status}},
    )

    if result.modified_count > 0:
        action = "removed" if is_remove else "set"
        await event.reply(f"User with ID {user_id_to_premium} is now {'not ' if is_remove else ''}a premium user.")
    else:
        await event.reply(f"User with ID {user_id_to_premium} not found.")


# Function to load user tokens from MongoDB
async def load_user_tokens():
    user_tokens = []
    async for user in user_tokens_collection.find():
        user_tokens.append(user)
    return user_tokens

SHORTENER_API_URL = f'{SHORTNER_URL}/api?api={SHORTNER_API}&url='

# Function to shorten a given URL
def shorten_url(original_url):
    try:
        response = requests.get(SHORTENER_API_URL + original_url)
        if response.status_code == 200:
            return response.json()['shortenedUrl']
        else:
            print(f"Failed to shorten URL: {response.text}")
    except Exception as e:
        print(f"Error occurred while shortening URL: {e}")
    return None

async def handle_message(m: Message):
    # Define the channel
    channel = f"{CHANNEL_USERNAME}"

    # Check if the user is a member of the channel
    check_channel = await is_user_on_chat(bot, channel, m.peer_id)
    if not check_channel:
        msg_text = f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐛𝐞𝐟𝐨𝐫𝐞 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭."
        btn_txt = "⚠️ 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 ⚠️"
        button = Button.url(btn_txt, f"https://t.me/{channel}")
        return await m.reply(msg_text, buttons=button)

    # Load user tokens from MongoDB
    user_tokens = await load_user_tokens()

    # Check if the user is verified or is an admin
    user_id = m.sender_id
    user = await user_tokens_collection.find_one({"user_id": user_id, "is_premium": True})
    is_admin = True if user else False
    
    token_verified = any(user['user_id'] == user_id and user['verified'] for user in user_tokens)

    if not is_admin and not token_verified:
        # Get the token for the user from user_tokens.json
        token = next((user['token'] for user in user_tokens if user['user_id'] == user_id), None)
        if token:
            verification_link = f"https://telegram.me/{BOT_USERNAME}?start={token}"
            shortened_verification_link = shorten_url(verification_link)

            # Create the verification button with the shortened verification link
            verification_button = Button.url("𝐕𝐞𝐫𝐢𝐟𝐲 𝐍𝐨𝐰", shortened_verification_link)

            # Create another button with a different link
            TUT_button_link = TUTORAL_VID_URL
            TUT_button = Button.url("𝐇𝐨𝐰 𝐓𝐨 𝐕𝐞𝐫𝐢𝐟𝐲", TUT_button_link)

            # Create a list of buttons organized into rows
            buttons = [
                [verification_button],  # First row with verification button
                [TUT_button]  # Second row with another button
            ]

            # Modify the message text to include the buttons
            message_text = (
                f"𝐏𝐥𝐞𝐚𝐬𝐞 𝐯𝐞𝐫𝐢𝐟𝐲 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐟𝐞𝐚𝐭𝐮𝐫𝐞.\n\n"
                f"𝐇𝐨𝐰 𝐓𝐨 𝐕𝐞𝐫𝐢𝐟𝐲...!\n𝟏. 𝐂𝐥𝐢𝐜𝐤 '𝐕𝐞𝐫𝐢𝐟𝐲 𝐍𝐨𝐰' 𝐁𝐮𝐭𝐭𝐨𝐧\n𝟐. 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞 𝐀𝐝 𝐏𝐫𝐨𝐜𝐞𝐬𝐬\n𝟑. 𝐒𝐡𝐨𝐫𝐭𝐞𝐧𝐞𝐫 𝐥𝐢𝐧𝐤 𝐫𝐞𝐝𝐢𝐫𝐞𝐜𝐭 𝐲𝐨𝐮 𝐭𝐨 𝐁𝐨𝐭\n𝟒. 𝐘𝐨𝐮 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐕𝐞𝐫𝐢𝐟𝐢𝐞𝐝\n\n"
                f"𝐈𝐟 𝐲𝐨𝐮 𝐃𝐨𝐧'𝐭 𝐔𝐧𝐝𝐞𝐫𝐬𝐭𝐚𝐧𝐝 𝐭𝐡𝐞𝐧 𝐜𝐥𝐢𝐜𝐤 '𝐇𝐨𝐰 𝐓𝐨 𝐕𝐞𝐫𝐢𝐟𝐲' 𝐁𝐮𝐭𝐭𝐨𝐧 𝐚𝐧𝐝 𝐖𝐚𝐭𝐜𝐡 𝐕𝐢𝐝𝐞𝐨\n\n𝐂𝐂: {CHANNEL_USERNAME}"
            )

            # Load the image URL for sending with the message
            image_url = VERIFY_IMAGE  # Replace this with your actual image URL

            # Send the message with the list view of buttons and the image
            return await m.reply(
                message_text,
                parse_mode='Markdown',
                buttons=buttons,
                file=image_url
            )

    # Skip spam check for admins
    if not is_admin:
        is_spam = db.get(m.sender_id)
        if is_spam:
            return await m.reply("𝐘𝐨𝐮 𝐚𝐫𝐞 𝐬𝐩𝐚𝐦𝐦𝐢𝐧𝐠. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝟏 𝐦𝐢𝐧𝐮𝐭𝐞 𝐚𝐧𝐝 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧.")

    # Continue with handling Terabox link
    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("𝐏𝐥𝐞𝐚𝐬𝐞 𝐞𝐧𝐭𝐞𝐫 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐔𝐑𝐋.")

    hm = await m.reply("𝐒𝐞𝐧𝐝𝐢𝐧𝐠 𝐲𝐨𝐮 𝐭𝐡𝐞 𝐦𝐞𝐝𝐢𝐚, 𝐩𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭...")

    count = db.get(f"check_{m.sender_id}")
    if count and int(count) > 30:
        return await hm.edit("𝐘𝐨𝐮 𝐚𝐫𝐞 𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐧𝐨𝐰. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐦𝐞 𝐛𝐚𝐜𝐤 𝐚𝐟𝐭𝐞𝐫 𝟑𝟎 𝐦𝐢𝐧𝐮𝐭𝐞𝐬 𝐨𝐫 𝐮𝐬𝐞 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐚𝐜𝐜𝐨𝐮𝐧𝐭.")

    shorturl = extract_code_from_url(url)
    if not shorturl:
        return await hm.edit("𝐒𝐞𝐞𝐦𝐬 𝐥𝐢𝐤𝐞 𝐲𝐨𝐮𝐫 𝐥𝐢𝐧𝐤 𝐢𝐬 𝐢𝐧𝐯𝐚𝐥𝐢𝐝.")

    data = get_data(url)
    if not data:
        return await hm.edit("𝐒𝐨𝐫𝐫𝐲! 𝐀𝐏𝐈 𝐢𝐬 𝐝𝐨𝐰𝐧 𝐨𝐫 𝐲𝐨𝐮𝐫 𝐥𝐢𝐧𝐤 𝐢𝐬 𝐛𝐫𝐨𝐤𝐞𝐧.")
    db.set(m.sender_id, time.monotonic(), ex=60)
    if (
        not data["file_name"].endswith(".mp4")
        and not data["file_name"].endswith(".mkv")
        and not data["file_name"].endswith(".Mkv")
        and not data["file_name"].endswith(".webm")
        and not data["file_name"].endswith(".MP4")
        and not data["file_name"].endswith(".mp4")
    ):
        return await hm.edit(
            f"𝐒𝐨𝐫𝐫𝐲! 𝐎𝐧𝐥𝐲 .𝐦𝐩𝟒, .𝐦𝐤𝐯, 𝐚𝐧𝐝 .𝐰𝐞𝐛𝐦 𝐟𝐢𝐥𝐞𝐬 𝐚𝐫𝐞 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐟𝐨𝐫 𝐝𝐨𝐰𝐧𝐥𝐨𝐚𝐝."
        )
        
    start_time = time.time()
    cansend = CanSend()

    async def progress_bar(current_downloaded, total_downloaded, state="Sending"):
        if not cansend.can_send():
            return
        bar_length = 20
        percent = current_downloaded / total_downloaded
        arrow = "★" * int(percent * bar_length)
        spaces = "☆" * (bar_length - len(arrow))

        elapsed_time = time.time() - start_time

        head_text = f"{state} `{data['file_name']}`"
        progress_bar = f"[{arrow + spaces}] {percent:.2%}"
        upload_speed = current_downloaded / elapsed_time if elapsed_time > 0 else 0
        speed_line = f"𝐒𝐩𝐞𝐞𝐝: **{get_formatted_size(upload_speed)}/s**"

        time_remaining = (
            (total_downloaded - current_downloaded) / upload_speed
            if upload_speed > 0
            else 0
        )
        time_line = f"𝐓𝐢𝐦𝐞 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: `{convert_seconds(time_remaining)}`"

        size_line = f"𝐒𝐢𝐳𝐞: **{get_formatted_size(current_downloaded)}** / **{get_formatted_size(total_downloaded)}**"

        await hm.edit(
            f"{head_text}\n{progress_bar}\n{speed_line}\n{time_line}\n{size_line}",
            parse_mode="markdown",
        )

    uuid = str(uuid4())
    thumbnail = download_image_to_bytesio(data["thumb"], "thumbnail.png")

    try:
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            file=data["direct_link"],
            thumb=thumbnail if thumbnail else None,
            progress_callback=progress_bar,
            caption=f"""
𝐅𝐢𝐥𝐞 𝐍𝐚𝐦𝐞: `{data['file_name']}`
𝐒𝐢𝐳𝐞: **{data["size"]}** 
𝐃𝐢𝐫𝐞𝐜𝐭 𝐋𝐢𝐧𝐤: [𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞](https://t.me/{BOT_USERNAME}?start={uuid})

@{CHANNEL_USERNAME}
""",
            supports_streaming=True,
            spoiler=True,
        )
    except telethon.errors.rpcerrorlist.WebpageCurlFailedError:
        download = await download_file(
            data["direct_link"], data["file_name"], progress_bar
        )
        if not download:
            return await hm.edit(
                f"𝐒𝐨𝐫𝐫𝐲! 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐅𝐚𝐢𝐥𝐞𝐝 𝐛𝐮𝐭 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐝𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐢𝐭 𝐟𝐫𝐨𝐦 [𝐡𝐞𝐫𝐞]({data['direct_link']}).",
                parse_mode="markdown",
            )
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            download,
            caption=f"""
𝐅𝐢𝐥𝐞 𝐍𝐚𝐦𝐞: `{data['file_name']}`
𝐒𝐢𝐳𝐞: **{data["size"]}** 
𝐃𝐢𝐫𝐞𝐜𝐭 𝐋𝐢𝐧𝐤: [𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞](https://t.me/{BOT_USERNAME}?start={uuid})

@{CHANNEL_USERNAME}
""",
            progress_callback=progress_bar,
            thumb=thumbnail if thumbnail else None,
            supports_streaming=True,
            spoiler=True,
        )
        try:
            os.unlink(download)
        except Exception as e:
            print(e)
    except Exception:
        return await hm.edit(
            f"𝐒𝐨𝐫𝐫𝐲! 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐅𝐚𝐢𝐥𝐞𝐝 𝐛𝐮𝐭 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐝𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐢𝐭 𝐟𝐫𝐨𝐦 [𝐡𝐞𝐫𝐞]({data['direct_link']}).",
            parse_mode="markdown",
        )
    try:
        os.unlink(download)
    except Exception as e:
        pass
    try:
        await hm.delete()
    except Exception as e:
        print(e)

    if shorturl:
        db.set(shorturl, file.id)
    if file:
        db.set(uuid, file.id)

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file.id],
                to_peer=m.chat.id,
                top_msg_id=m.id,
                drop_author=True,
                noforwards=False,
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        db.set(m.sender_id, time.monotonic(), ex=60)
        db.set(
            f"check_{m.sender_id}",
            int(count) + 1 if count else 1,
            ex=1800,
        )

bot.start(bot_token=BOT_TOKEN)
bot.run_until_disconnected()
