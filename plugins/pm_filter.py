# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import datetime
import pytz

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from datetime import datetime
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
QUERY = {}
SELECT = {}

SPELL_MODE = True

PM_FILTER_MODE = True
max_clicks = 1
LANG = {}

now = datetime.now()
tz = pytz.timezone('asia/kolkata')
your_now = now.astimezone(tz)
hour = your_now.hour
if 0 <= hour <12:
    lallus = "Gᴏᴏᴅ ᴍᴏʀɴɪɴɢ"
elif 12 <= hour <15:
    lallus = 'Gᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ'
elif 15 <= hour <20:
    lallus = 'Gᴏᴏᴅ ᴇᴠᴇɴɪɴɢ'
else:
    lallus = 'Gᴏᴏᴅ ɴɪɢʜᴛ'

TEMP_TXT = """🏷 𝖳𝗂𝗍𝗅𝖾: {title} 
🔮 𝖸𝖾𝖺𝗋: {year} 
⭐️ 𝖱𝖺𝗍𝗂𝗇𝗀𝗌: {rating}/ 10
🎭 𝖦𝖾𝗇𝖾𝗋𝗌: {genres}"""

SPELL_TXT = """➼ 𝑯𝒆𝒚 {mention}

𝚄𝚛 𝚛𝚎𝚚𝚞𝚎𝚜𝚝𝚎𝚍 𝚖𝚘𝚟𝚒𝚎𝚜 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐 𝚒𝚜 𝚒𝚗𝚌𝚘𝚛𝚛𝚎𝚌𝚝 𝚝𝚑𝚎 𝚌𝚘𝚛𝚛𝚎𝚌𝚝 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐𝚜 𝚒𝚜 𝚐𝚒𝚟𝚎𝚗 𝚋𝚎𝚕𝚕𝚘𝚠

➣ 𝚜𝚙𝚎𝚕𝚕𝚒𝚗𝚐: <m>{title}</m>

𝙲𝙷𝙴𝙲𝙺 𝚃𝙷𝙴 𝙸𝙽𝚂𝚃𝚁𝚄𝙲𝚃𝙸𝙾𝙽𝚂

➪ Oɴʟʏ Oᴛᴛ Rᴇʟᴇᴀsᴇ Mᴏᴠɪᴇ Is Aᴠᴀɪʟᴀʙʟᴇ
➪ Mᴀᴋᴇ Sᴜʀᴇ Tʜᴇ Sᴘᴇʟʟɪɴɢ Is Cᴏʀʀᴇᴄᴛ
➪ Nᴏ PʀᴇDᴠD, CᴀᴍRɪᴘ Aᴠᴀɪʟᴀʙʟᴇ Hᴇʀᴇ
"""

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    req = message.from_user.id if message.from_user else 0
    if k == False:
        settings = await get_settings(message.chat.id)
        if settings['text_ffilter']:
            content = message.text
            if content.startswith("/") or content.startswith("#"): return
            search = message.text
            temp_files, temp_offset, total_results = await get_search_results(query=search.lower(), offset=0, filter=True)
            if int(req) not in [message.from_user.id, 0]:
                return await message.answer("oKda", show_alert=True)
            if total_results == 0:
                reqst_gle = search.replace(" ", "-")
                return await message.reply(text=f"<b>Hey {message.from_user.mention}\n\nYour requested movie {search} spelling is incrroct or check this movie released in ott 🥺 Clck the google button and check spelling</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍Sᴇᴀʀᴄʜ Gᴏᴏɢʟᴇ🔎", url=f"https://www.google.com/search?q={search}")]]))
            else:
                 user = message.from_user.id
                 key = f"{message.id}"
                 userid = user
                 LANG[key] = search
                 btn = [[
                     InlineKeyboardButton("🔮Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Lᴀɴɢᴜᴀɢᴇ ↓🔮  ", callback_data=f"lang#{key}#{userid}#unknown")
                 ],[
                     InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#{key}#{userid}#eng"),
                     InlineKeyboardButton("Tᴀᴍɪʟ", callback_data=f"lang#{key}#{userid}#tam"),
                     InlineKeyboardButton("Hɪɴᴅɪ", callback_data=f"lang#{key}#{userid}#hin")
                 ],[
                     InlineKeyboardButton("Kᴀɴɴᴀᴅᴀ", callback_data=f"lang#{key}#{userid}#kan"),
                     InlineKeyboardButton("Tᴇʟᴜɢᴜ", callback_data=f"lang#{key}#{userid}#tel")
                 ],[
                     InlineKeyboardButton("Mᴀʟᴀʏᴀʟᴀᴍ", callback_data=f"lang#{key}#{userid}#mal")
                 ],[
                     InlineKeyboardButton("✒️Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ✒️", callback_data='tutorial')
                 ]]
                
                 await message.reply_text(text=f"<b>Fᴏᴜɴᴅ Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ {search} {total_results} Rᴇꜱᴜʟᴛꜱ Aᴠᴀɪʟᴀʙʟᴇ...😇\n\nCʟɪᴄᴋ Tʜᴇ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴ Fᴏʀ Gᴇᴛ Tʜᴇ Mᴏᴠɪᴇ👇\n\nPʟᴇᴀꜱ Sᴇʟᴇᴄᴛ Tʜᴇ Lᴀɴɢᴀᴜɢᴇ Wʜᴀᴛ U Wᴀɴᴛ ɪᴛ🕵️</b>", reply_markup=InlineKeyboardMarkup(btn))
        if settings['auto_ffilter']:
            await auto_filter(client, message)
        if settings['grp_ffilter']:
            await grp_filter(client, message)

@Client.on_callback_query(filters.regex(r"^hnext"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🎬[{get_size(file.file_size)}]🔗 {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton(f'Yᴏᴜʀ Fɪʟᴇ Is Rᴇᴀᴅʏ👇', callback_data='urfile')
           
        ]
    )
    btn.insert(1,
        [
            InlineKeyboardButton(f'ғɪʟᴇs: {len(files)}', 'dupe'),
            InlineKeyboardButton(text="Sᴇʟᴇᴄᴛ", callback_data=f'select_{req}_{key}_{offset}')
        ]
    )

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("☜︎︎︎ ʙᴀᴄᴋ", callback_data=f"hnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ☞︎︎︎", callback_data=f"hnext_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("☜︎︎︎ ʙᴀᴄᴋ", callback_data=f"hnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ☞︎︎︎", callback_data=f"hnext_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    _, key, userid, language = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer("Not For You Brother", show_alert=True)
    if language == "unknown":
        return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
    movi = LANG.get(key)
    if not movi:
        return await query.answer("Old Message", show_alert=True)
    if language != "home":
        movie = f"{movi} {language}"
    else:
        await query.message.delete()
        return
    files, offset, total_results = await get_search_results(query=movie, offset=0, filter=True)
    text = "Click Here"
    if files:
        key = f"{query.message.chat.id}-{query.message.id}"
        QUERY[key] = movie 
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=pmfilter_{key}")
    else:
        await query.answer(f"Sᴏʀʀʏ Bʀᴏ Tʜɪꜱ Lᴀɴɢᴜᴀɢᴇ Fᴏʀ {movi}Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ Cʟɪᴄᴋ Oᴛʜᴇʀ Lᴀɴɢᴜᴀɢᴇ Oʀ Cʟᴏꜱᴇ Tʜɪs", show_alert=True)

@Client.on_callback_query(filters.regex(r"^btnext"))
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
        text += f"<i>\n\n<a href='https://t.me/{temp.U_NAME}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i>"
    if 0 < offset <= 6:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 6
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("◀️ BACK", callback_data=f"btnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")],
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ▶️", callback_data=f"btnext_{req}_{key}_{n_offset}")],
       )
    else:
        btn.append(
            [
                InlineKeyboardButton("◀️ BACK", callback_data=f"btnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ▶️", callback_data=f"btnext_{req}_{key}_{n_offset}")
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
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
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
            f_caption = f"{files.file_name}"

        try:
            if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("pmfilter"):
        _, key, user = query.data.split("_")
        if int(user) not in [query.from_user.id, 0]:
            return await query.answer("Not For You", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=pm_{key}")
        
    elif query.data.startswith("checksub"):
        if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('Channel Updates🍿', url="https://t.me/MOVIES_DATA_UPDATES"),
            InlineKeyboardButton('Share now🚩', url='https://t.me/share/url?url=https%3A//t.me/Cat_movie_bot')
            ],[
            InlineKeyboardButton('Demo✨', url='https://t.me/BYPASS_DEMO_VIDEO')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('ᴀ ғɪʟᴛᴇʀ', callback_data='autofilter'),
            InlineKeyboardButton('ᴍ ғɪʟᴛᴇʀ', callback_data='manuelfilter')
            ],[
            InlineKeyboardButton('Cᴏɴɴᴇᴄᴛ', callback_data='coct'),
            InlineKeyboardButton('Aᴅᴍɪɴ', callback_data='admin')
            ],[
            InlineKeyboardButton('Tᴇxᴛ Fɪʟᴛᴇʀ', callback_data='txtfltr'),
            InlineKeyboardButton('Gʀᴘ Fɪʟᴛᴇʀ', callback_data='grpfltr')
            ],[
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close_data')
            ],[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('sᴛᴀᴛᴜs', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "txtfltr":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FLT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "grpfltr":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFLT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Bᴜᴛᴛᴏɴs', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Aᴅᴍɪɴ', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("exit"):
        ident, req, key, offset = query.data.split("_")    
        try:
            offset = int(offset)
        except:
            offset = 0
        search = BUTTONS.get(key)
        if not search:
            await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
            return

        files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
        try:
            n_offset = int(n_offset)
        except:
            n_offset = 0

        if not files:
            return
        settings = await get_settings(query.message.chat.id)
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"🎬[{get_size(file.file_size)}]🔗 {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"),
                    ),
                ]
                for file in files
            ]

        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("☜︎︎︎ Bᴀᴄᴋ", callback_data=f"hnext_{req}_{key}_{off_set}"),
                 InlineKeyboardButton(f"Pᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                      callback_data="pages")]
            )
            btn.insert(0, 
                [
                 InlineKeyboardButton(f'Yᴏᴜʀ Fɪʟᴇ Is Rᴇᴀᴅʏ👇', callback_data='urfile')        
                ]
            )
            btn.insert(1,
                [
                 InlineKeyboardButton(f'Fɪʟᴇs: {len(files)}', 'file'),
                 InlineKeyboardButton(text="Sᴇʟᴇᴄᴛ", callback_data=f'select_{req}_{key}_{offset}')
                ]
            )        
        elif off_set is None:
            btn.append(
                [InlineKeyboardButton(f"Pᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                 InlineKeyboardButton("Nᴇxᴛ ☞︎︎︎", callback_data=f"hnext_{req}_{key}_{n_offset}")])
            btn.insert(0, 
                [
                 InlineKeyboardButton(f'⚔️ {search} ⚔️', url=f"https://imdb.com/search?q={search}")        
                ]
            )
            btn.insert(1,
                [
                 InlineKeyboardButton(f'Fɪʟᴇs: {len(files)}', 'file'),
                 InlineKeyboardButton(text="Sᴇʟᴇᴄᴛ", callback_data=f'select_{req}_{key}_{offset}')
                ]
            )        
        else:
            btn.append(
                [
                    InlineKeyboardButton("☜︎︎︎ Bᴀᴄᴋ", callback_data=f"hnext_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"Pᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                    InlineKeyboardButton("Nᴇxᴛ ☞︎︎︎", callback_data=f"hnext_{req}_{key}_{n_offset}")
                ],
            ) 
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'⚔️ {search} ⚔️', url=f"https://imdb.com/search?q={search}")          
                ]
            )
            btn.insert(1,
                [
                    InlineKeyboardButton(f'ғɪʟᴇs: {len(files)}', 'file'),
                    InlineKeyboardButton(text="Select", callback_data=f'select_{req}_{key}_{offset}')
                ]
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
            
    elif query.data.startswith("select"):
        query_data = query.data.split("_")
        
        ident, req, key, offset = query_data
        
        try:
            offset = int(offset)
        except:
            offset = 0
        search = BUTTONS.get(key)
        if not search:
            await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
            return

        files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
        try:
            n_offset = int(n_offset)
        except:
            n_offset = 0

        if not files:
            return
        
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🎬[{get_size(file.file_size)}]🔗 {file.file_name}", callback_data=f'sel#{file.file_id}'
                ),
            ]
            for file in files
        ]

        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("☜︎︎︎ Bᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                 InlineKeyboardButton(f"Pᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                      callback_data="pages")]
            )
        elif off_set is None:
            btn.append(
                [InlineKeyboardButton(f"Hᴏᴡ ᴛᴏ Sᴇʟᴇᴄᴛ", callback_data="pages")])            
        else:
            btn.append(
                [
                    InlineKeyboardButton("Hᴏᴡ Tᴏ Sᴇʟᴇᴄᴛ", callback_data=f"next_{req}_{key}_{off_set}")
                ],
            )
        btn.insert(0, [InlineKeyboardButton("Exɪᴛ", callback_data=f'exit_{req}_{key}_{offset}'), InlineKeyboardButton("Sᴇɴᴅ", callback_data='send')])
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )    
        except MessageNotModified:
            pass

    elif query.data.startswith("sel"):
        ident, file_id = query.data.split("#")
        ay = []
        try:
            SELECT[query.from_user.id].append(file_id)
        except KeyError:
            ay.append(file_id)
            SELECT[query.from_user.id] = ay
        original_message = query.message
        original_markup = original_message.reply_markup

        updated_buttons = []
        for row in original_markup.inline_keyboard:
            updated_row = []
            for button in row:
                if button.callback_data == query.data:
                    updated_button = InlineKeyboardButton("✔️", callback_data=button.callback_data)
                else:
                    updated_button = button
                updated_row.append(updated_button)
            updated_buttons.append(updated_row)

        
        updated_markup = InlineKeyboardMarkup(updated_buttons)

        # Edit the message with the updated inline keyboard markup
        await client.edit_message_reply_markup(
            chat_id=original_message.chat.id,
            message_id=original_message.id,
            reply_markup=updated_markup
        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["botpm"] else '✘ Oғғ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('TEXT-FILTER',
                                         callback_data=f'setgs#auto_ffilter#{settings["text_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["text_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#text_ffilter#{settings["text_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('GRP-FILTER',
                                         callback_data=f'setgs#grp_ffilter#{settings["grp_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["grp_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#grp_ffilter#{settings["grp_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    if query.data == "send":
        try:
            files = SELECT[query.from_user.id]
        except IndexError:
            return await query.answer(text="You Haven't Selected Any Files", show_alert=True)
        for jig in files:
            files_ = await get_file_details(jig)
            files = files_[0]
            title = files.file_name
            size = get_size(files.file_size)
            f_caption = files.caption
            try:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=jig,
                    caption=f_caption
                    
                 )
            except UserIsBlocked:
                await query.answer('Unblock the bot mahn !', show_alert=True)
                break
                return 
            except Exception as e:
                await query.answer(e, show_alert=True)
                break
                return 
        await query.answer('Check PM, I have sent files in pm', show_alert=True)
        del SELECT[query.from_user.id]        
    await query.answer()

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if SPELL_CHECK_REPLY:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message # msg will be callback query
        search, files, offset, total_results = spoll
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🎬[{get_size(file.file_size)}]🔗 {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"),
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"),
                ),
            ]
            for file in files
        ]

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"ᴘᴀɢᴇs 1/{round(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="Nᴇxᴛ ☞︎︎︎",callback_data=f"hnext_{req}_{key}_{offset}")]
        )
        btn.insert(0, 
            [
             InlineKeyboardButton(f'Yᴏᴜʀ Fɪʟᴇ Is Rᴇᴀᴅʏ👇', callback_data='urfile')        
            ]
        )
        btn.insert(1,
            [
             InlineKeyboardButton(f'ғɪʟᴇs: {len(files)}', 'dupe'),
             InlineKeyboardButton(text="Sᴇʟᴇᴄᴛ", callback_data=f'select_{req}_{key}_{offset}')
            ]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="Nᴏ Mᴏʀᴇ Pᴀɢᴇs Aᴠᴀɪʟᴀʙʟᴇ",callback_data="pages")]
        )
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.insert(0, 
            [
             InlineKeyboardButton(f'Yᴏᴜʀ Fɪʟᴇ Is Rᴇᴀᴅʏ👇', callback_data='urfile')        
            ]
        )
        btn.insert(1,
            [
             InlineKeyboardButton(f'ғɪʟᴇs: {len(files)}', 'dupe'),
             InlineKeyboardButton(text="Sᴇʟᴇᴄᴛ", callback_data=f'select_{req}_{key}_{offset}')
            ]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if IMDB else None
    if imdb:
        cap = IMDB_TEMPLATE.format(
            query = search, 
            title = imdb['title'], 
            votes = imdb['votes'], 
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'], 
            localized_title = imdb['localized_title'],
            kind = imdb['kind'], 
            imdb_id = imdb["imdb_id"], 
            cast = imdb["cast"], 
            runtime = imdb["runtime"], 
            countries = imdb["countries"],
            certificates = imdb["certificates"], 
            languages = imdb["languages"],
            director = imdb["director"], 
            writer = imdb["writer"], 
            producer = imdb["producer"], 
            composer = imdb["composer"], 
            cinematographer = imdb["cinematographer"], 
            music_team = imdb["music_team"], 
            distributors = imdb["distributors"],
            release_date = imdb['release_date'], 
            year = imdb['year'],
            genres = imdb['genres'], 
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'], 
            url = imdb['url'],
            **locals()
        )
    else:
        cap = f"👋Hʏ {message.from_user.mention}\n\n✒️Tɪᴛʟᴇ : {search}\n📁Fɪʟᴇs : <code>{total_results}</code>\n\n🗳️Uᴘʟᴏᴀᴅᴇᴅ: {message.chat.title}"
    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            m=await message.reply_text("sᴇᴀʀᴄʜɪɴɢ ᴍᴏᴠɪᴇs ғᴏʀ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ")
            await asyncio.sleep(1)
            await m.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        s=await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(100)
        await s.edit_text(
            text=f"Fɪʟᴛᴇʀ Cʟᴏsᴇᴅ 🗑️\n\n✒️Tɪᴛʟᴇ : {search}\n📌 Rᴇǫᴜᴇsᴛᴇᴅ Bʏ : {message.from_user.mention}\n🗳️Uᴘʟᴏᴀᴅᴇᴅ Bʏ :{message.chat.title}")           
    
    if spoll:
        await msg.message.delete()

async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "",
        msg.text,
        flags=re.IGNORECASE,
    )  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(
        r".*(imdb|wikipedia).*", re.IGNORECASE
    )  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [
        re.sub(
            r"\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)",
            "",
            i,
            flags=re.IGNORECASE,
        )
        for i in gs
    ]
    if not gs_parsed:
        reg = re.compile(
            r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*", re.IGNORECASE
        )  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(
        dict.fromkeys(gs_parsed)
    )  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(
                mov.strip(), bulk=True
            )  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get("title") for movie in imdb_s]
    movielist += [
        (re.sub(r"(\-|\(|\)|_)", "", i, flags=re.IGNORECASE)).strip() for i in gs_parsed
    ]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply(
            "I couldn't find nothing related to that. Check your spelling"
        )
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie.strip(),
                callback_data=f"spolling#{user}#{k}",
            )
        ]
        for k, movie in enumerate(movielist)
    ]
    btn.append(
        [
            InlineKeyboardButton(
                text="Close", callback_data=f"spolling#{user}#close_spellcheck"
            )
        ]
    )
    __msg = await msg.reply(
        "I couldn't find anything related to that Okay\nDid you mean any one of these?",
        reply_markup=InlineKeyboardMarkup(btn),
    )


async def grp_filter(client, msg, spoll=False):
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
            [InlineKeyboardButton(text=f"Pᴀɢᴇs 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="Nᴇxᴛ ☞︎︎︎", callback_data=f"btnext_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="Nᴏ Mᴏʀᴇ Pᴀɢᴇs Aᴠᴀɪʟᴀʙʟᴇ", callback_data="pages")]
        )
        btn.insert(
            [InlineKeyboardButton(text="Select", callback_data=f'select_{req}_{key}_{offset}')])
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
        msg += f"<i>\n\n<a href='https://t.me/{temp.U_NAME}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i>"
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
            cap += f"<b><i>\n\n<a href='https://t.me/{temp.U_NAME}?start=file_{file.file_id}'>⏩ [{get_size(file.file_size)}] {file.file_name}</a></i></b>"
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.message.delete()

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

@Client.on_message(filters.private & filters.text)
async def private(client, message):
    await auto_filter(client, message)
