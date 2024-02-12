
import re
import ast
import math
import random
import asyncio

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, PICS, REQ_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from plugins.clone import clonedme
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

SPELL_MODE = True

QUERY = {}

PM_FILTER_MODE = True
max_clicks = 1
LANG = {}

SPELL_TXT = """➼ 𝑯𝒆𝒚 {mention}
𝚄𝚛 𝚛𝚎𝚚𝚞𝚎𝚜𝚝𝚎𝚍 𝚖𝚘𝚟𝚒𝚎𝚜 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐 𝚒𝚜 𝚒𝚗𝚌𝚘𝚛𝚛𝚎𝚌𝚝 𝚝𝚑𝚎 𝚌𝚘𝚛𝚛𝚎𝚌𝚝 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐𝚜 𝚒𝚜 𝚐𝚒𝚟𝚎𝚗 𝚋𝚎𝚕𝚕𝚘𝚠

➣ 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐: {title}
➣ 𝙳𝚊𝚝𝚎: {year}

𝐘𝐨𝐮𝐫 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐞𝐝 𝐌𝐨𝐯𝐢𝐞 𝐒𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐈𝐬 𝐈𝐧𝐜𝐨𝐫𝐫𝐞𝐜𝐭 𝐂𝐡𝐞𝐜𝐤 𝐒𝐩𝐞𝐥𝐥𝐢𝐧𝐠 𝐀𝐧𝐝 𝐀𝐬𝐤 𝐀𝐠𝐚𝐢𝐧 𝐎𝐑 𝐂𝐡𝐞𝐜𝐤 𝐓𝐡𝐢𝐬 𝐌𝐨𝐯𝐢𝐞 𝐎𝐭𝐭 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 𝐎𝐫 𝐍𝐨𝐭
"""

TEMP_TXT = """🏷 𝖳𝗂𝗍𝗅𝖾: {title} 
🔮 𝖸𝖾𝖺𝗋: {year} 
⭐️ 𝖱𝖺𝗍𝗂𝗇𝗀𝗌: {rating}/ 10
🎭 𝖦𝖾𝗇𝖾𝗋𝗌: {genres}"""


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    await auto_filter(client, message)
       
@Client.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):

    btn = [[
        InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Lᴀɴɢᴜᴀɢᴇ ↓", callback_data=f"lang#unknown")
    ],[
        InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#eng"),
        InlineKeyboardButton("Tᴀᴍɪʟ", callback_data=f"lang#tam"),
        InlineKeyboardButton("Hɪɴᴅɪ", callback_data=f"lang#hin")
    ],[
        InlineKeyboardButton("Kᴀɴɴᴀᴅᴀ", callback_data=f"lang#kan"),
        InlineKeyboardButton("Tᴇʟᴜɢᴜ", callback_data=f"lang#tel")
    ],[
        InlineKeyboardButton("Mᴀʟᴀʏᴀʟᴀᴍ", callback_data=f"lang#mal")
    ],[
        InlineKeyboardButton("Mᴜʟᴛɪ Aᴜᴅɪᴏ", callback_data=f"lang#multi"),
        InlineKeyboardButton("Dᴜᴀʟ Aᴜᴅɪᴏ", callback_data=f"lang#dual")
    ],[
        InlineKeyboardButton("Gᴏ Bᴀᴄᴋ", callback_data=f"lang#home")
    ]]
    try:
        await query.message.edit_text(text= "select language",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^pmnext"))
async def pmnexter(bot, query):
    ident, req, key, offset = query.data.split("_")
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=offset, filter=True, max_results=5)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    imdb = await get_poster(search)
    btn = []
    text = TEMP_TXT.format(title=imdb.get('title'), genres=imdb.get('genres'), year=imdb.get('year'), rating=imdb.get('rating'))
    me = await bot.get_me() 
    for file in files:
        text += f"<i>\n\n<a href='https://t.me/{me.username}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i>"
    if 0 < offset <= 6:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 6
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("◀️ BACK", callback_data=f"pmnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")],
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ▶️", callback_data=f"pmnext_{req}_{key}_{n_offset}")],
       )
    else:
        btn.append(
            [
                InlineKeyboardButton("◀️ BACK", callback_data=f"pmnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ▶️", callback_data=f"pmnext_{req}_{key}_{n_offset}")
            ],
        )
        btn.append(
            [InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Lᴀɴɢᴜᴀɢᴇ", callback_data="select_lang")]
        )
    await bot.edit_message_text(query.message.chat.id, query.message.id, text, reply_markup=InlineKeyboardMarkup(btn))  

@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    language = query.data.split("#")
    if language == "unknown":
        return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
    movie = LANG.get(query.from_user.id)
    if not movie:
        return await query.answer("old message", show_alert=True)
    if language != "home":
        movie = f"{movie} {language}"
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)

    if not files:
        return
    imdb = await get_poster(search)
    btn = []
    text = TEMP_TXT.format(title=imdb.get('title'), genres=imdb.get('genres'), year=imdb.get('year'), rating=imdb.get('rating'))
    me = await bot.get_me() 
    for file in files:
        text += f"<i>\n\n<a href='https://t.me/{me.username}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i>"
    if 0 < offset <= 6:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 6
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("◀️ BACK", callback_data=f"pmnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")],
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ▶️", callback_data=f"pmnext_{req}_{key}_{n_offset}")],
       )
    else:
        btn.append(
            [
                InlineKeyboardButton("◀️ BACK", callback_data=f"pmnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ▶️", callback_data=f"pmnext_{req}_{key}_{n_offset}")
            ],
        )
        btn.append(
            [InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Lᴀɴɢᴜᴀɢᴇ", callback_data="select_lang")]
        )
    await bot.edit_message_text(query.message.chat.id, query.message.id, text, reply_markup=InlineKeyboardMarkup(btn))  



@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        me = await client.get_me()
        user_nme = me.username
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{file_name}"
        try:
            if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{clonedme.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{clonedme.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Cʜᴇᴄᴋ PM, I ʜᴀᴠᴇ sᴇɴᴛ ғɪʟᴇs ɪɴ ᴘᴍ', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{user_nme}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{user_nme}?start={ident}_{file_id}")

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True, max_results=5)
            if not files:
                if SPELL_MODE:  
                    reply = search.replace(" ", "+")
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔍ꜱᴇᴀʀᴄʜ ɢᴏᴏɢʟ🔎", url=f"https://google.com/find?q={reply}")
                    ]])
                    imdb=await get_poster(search)
                    if imdb and imdb.get('poster'):
                        lallu=await message.reply_text(SPELL_TXT.format(mention=message.from_user.mention, query=search, title=imdb.get('title'), genres=imdb.get('genres'), year=imdb.get('year'), rating=imdb.get('rating'), short=imdb.get('short_info'), url=imdb['url']), reply_markup=reply_markup)
                        await asyncio.sleep(200)                   
                        await lallu.delete()
                        return
                    else:
                        return
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        btn = []
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        btn = []
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ▶️", callback_data=f"pmnext_{req}_{key}_{offset}")]
        )
        btn.insert(0, [
             InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Lᴀɴɢ", callback_data=f"select_lang")
        ])
    else:
        btn.append(
            [InlineKeyboardButton(text="Nᴏ Mᴏʀᴇ Pᴀɢᴇs Aᴠᴀɪʟᴀʙʟᴇ", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        msg = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        me = await client.get_me() 
    for file in files:
        msg += f"<i>\n\n<a href='https://t.me/{me.username}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i>"
    else:
        cap = f"<b>Hᴇʏ {message.from_user.mention} Yᴏᴜʀ Rᴇǫᴜᴇsᴛᴇᴅ Fɪʟᴇ Fᴏʀ {search} Is ʀᴇᴀᴅʏ Tᴏ Dᴏᴡɴʟᴏᴀᴅ Cʟɪᴄᴋ ᴛʜᴇ ʟɪɴᴋ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ🤓</b>"
    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(photo=imdb.get('poster'), caption=msg[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            me = await client.get_me() 
        for file in files:
            cap += f"\n\n<a href='https://t.me/{temp.U_NAME}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a>"
            
    else:
        me = await client.get_me() 
        for file in files:
            cap += f"<b><i>\n\n<a href='https://t.me/{me.username}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i></b>"
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.message.delete()
