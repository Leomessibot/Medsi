import re
import logging

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from database.ia_filterdb import get_file_details

from info import API_ID, API_HASH, ADMINS, CUSTOM_FILE_CAPTION
from info import DATABASE_URI as MONGO_URL

CLONE_FILE_CHANNEL = "-1002193382677"


mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["cloned_bots"]

expired_bots = []

class clonedme(object):
    ME = None
    U_NAME = None
    B_NAME = None

@Client.on_message(filters.command('clone'))
async def clone_menu(client, message):
    if CLONE_MODE == False:
        return 
    if await db.is_clone_exist(message.from_user.id):
        return await message.reply("**ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴏɴᴇᴅ ᴀ ʙᴏᴛ ᴅᴇʟᴇᴛᴇ ғɪʀsᴛ ɪᴛ ʙʏ /deleteclone**")
    else:
        pass
    techvj = await client.ask(message.chat.id, "<b>1) sᴇɴᴅ <code>/newbot</code> ᴛᴏ @BotFather\n2) ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ꜰᴏʀ ʏᴏᴜʀ ʙᴏᴛ.\n3) ɢɪᴠᴇ ᴀ ᴜɴɪǫᴜᴇ ᴜsᴇʀɴᴀᴍᴇ.\n4) ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ.\n5) ꜰᴏʀᴡᴀʀᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>")
    if techvj.text == '/cancel':
        await techvj.delete()
        return await message.reply('<b>ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss 🚫</b>')
    if techvj.forward_from and techvj.forward_from.id == 93372553:
        try:
            bot_token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", techvj.text)[0]
        except:
            return await message.reply('<b>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ 😕</b>')
    else:
        return await message.reply('<b>ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ @BotFather 😑</b>')
    user_id = message.from_user.id
    msg = await message.reply_text("**👨‍💻 ᴡᴀɪᴛ ᴀ ᴍɪɴᴜᴛᴇ ɪ ᴀᴍ ᴄʀᴇᴀᴛɪɴɢ ʏᴏᴜʀ ʙᴏᴛ ❣️**")
    try:
        vj = Client(
            f"{bot_token}", API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "clone_plug"}
        )
        await vj.start()
        bot = await vj.get_me()
        await db.add_clone_bot(bot.id, user_id, bot_token)
        await msg.edit_text(f"<b>sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴏɴᴇᴅ ʏᴏᴜʀ ʙᴏᴛ: @{bot.username}.\n\nʏᴏᴜ ᴄᴀɴ ᴄᴜsᴛᴏᴍɪsᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ʙʏ /settings ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ</b>")
    except BaseException as e:
        await msg.edit_text(f"⚠️ <b>Bot Error:</b>\n\n<code>{e}</code>\n\n**Kindly forward this message to @KingVJ01 to get assistance.**")

async def get_bot():
    await ai.start()
    crazy = await ai.get_me()
    await ai.stop()
    return crazy


@Client.on_message(filters.command("clonedbots") & filters.private)
async def cloned_bots_list(client, message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        bots = list(mongo_db.bots.find({'user_id': user_id}))

        if len(bots) == 0:
            await message.reply_text("You haven't cloned any bots yet.")
            return

        text = "<b>Your cloned bots:</b>\n\n"

        for bot in bots:
            text += f"- @{bot['username']} ({bot['name']})\n"
            text += f"  Bot ID: {bot['bot_id']}\n"
            text += f"  Token: {bot['token']}\n"
            text += "\n"

        await message.reply_text(text)
    except Exception as e:
        logging.exception("𝙴𝚛𝚛𝚘𝚛 𝚆𝚑𝚒𝚕𝚎 𝙷𝚊𝚗𝚍𝚕𝚒𝚗𝚐 𝙲𝚕𝚘𝚗𝚎𝚍 𝙱𝚘𝚝𝚜 𝙲𝚘𝚖𝚖𝚊𝚗𝚍.")

@Client.on_message(filters.command('cloned_count') & filters.private)
async def cloned_count(client, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.reply_text("𝚈𝚘𝚞 𝙰𝚛𝚎 𝙽𝚘𝚝 𝙰𝚞𝚝𝚑𝚘𝚛𝚒𝚣𝚎𝚍 𝚃𝚘 𝚄𝚜𝚎 𝚃𝚑𝚒𝚜 𝙲𝚘𝚖𝚖𝚊𝚗𝚍.")
        return
    cloned_bots = mongo_db.bots.find()
    count = cloned_bots.count()
    if count == 0:
        await message.reply_text("𝙽𝚘 𝙱𝚘𝚝𝚜 𝙷𝚊𝚟𝚎 𝙱𝚎𝚎𝚗 𝙲𝚕𝚘𝚗𝚎𝚍 𝚈𝚎𝚝.")
    else:
        bot_usernames = [f"@{bot['username']}" for bot in cloned_bots]
        bot_usernames_text = '\n'.join(bot_usernames)
        await message.reply_text(f"{count} bots have been cloned:\n\n{bot_usernames_text}")

@Client.on_message(filters.command(["removebot"]) & filters.user(ADMINS))
async def remove_bot(client: Client, message: Message):
    bot_username = message.text.split(" ", maxsplit=1)[1].strip()
    bot_data = mongo_db.bots.find_one_and_delete({"username": bot_username})

    if bot_data:
        bot_id = bot_data["bot_id"]
        cloned_sessions = mongo_db.cloned_sessions.find({"bot_id": bot_id})
        if cloned_sessions.count() > 0:
            for session in cloned_sessions:
                await session.stop()
                mongo_db.cloned_sessions.delete_one({"_id": session["_id"]})
        await message.reply_text(f"Bot @{bot_username} removed successfully.")
    else:
        await message.reply_text(f"Bot @{bot_username} is not in the cloned bots list.")

@Client.on_message(filters.command("deletecloned") & filters.private)
async def delete_cloned_bot(client, message):
    try:
        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', message.text, re.IGNORECASE)
        bot_token = bot_token[0] if bot_token else None
        bot_id = re.findall(r'\d[0-9]{8,10}', message.text)

        cloned_bot = mongo_collection.find_one({"token": bot_token})
        if cloned_bot:
            mongo_collection.delete_one({"token": bot_token})
            await message.reply_text("The cloned bot has been removed from the list and its details have been removed from the database.")
        else:
            await message.reply_text("The bot token provided is not in the cloned list.")
    except Exception as e:
        logging.exception("Error while deleting cloned bot.")
        await message.reply_text("An error occurred while deleting the cloned bot.")
        
async def restart_bots():
    logging.info("Restarting all bots........")
    bots = list(mongo_db.bots.find())
    for bot in bots:
        bot_token = bot['token']
        try:
            ai = Client(
                f"{bot_token}", API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "clone_plug"},
            )
            await ai.start()
            logging.info(f"Bot @{ai.username} restarted.")
        except Exception as e:
            logging.exception(f"Error while restarting bot with token {bot_token}: {e}")
    #logging.info("All bots restarted.")

@Client.on_message(filters.command("restartall") & filters.user(ADMINS))
async def on_restart_all_bots(client: Client, message: Message):
    logging.info("Received restart command.")
    await message.reply_text("ʀᴇꜱᴛᴀʀᴛɪɴɢ ᴀʟʟ ʙᴏᴛꜱ....🏹")
    await restart_bots()
    await message.reply_text("ᴀʟʟ ʙᴏᴛꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇꜱᴛᴀʀᴛᴇᴅ 🔋")  
