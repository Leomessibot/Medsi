from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN

tobot = Client(name="clone-assist",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,             
             workers=300
             )
