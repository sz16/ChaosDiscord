# --- Logging ---
import utils.setup_log as setup_log
import logging
setup_log.setup_logging()
log = logging.getLogger(__name__)

# --- Env ---
# --- Firebase ---
import os, json
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, db
firebase_key = os.getenv("FIREBASE_KEY")
database_url = os.getenv("FIREBASE_URL")
#print(firebase_key, database_url)
if firebase_key and database_url:
    service_account_info = json.loads(firebase_key)
    db_url = database_url

    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred, {"databaseURL": db_url})
else:
    if not firebase_key:
        log.error("FIREBASE_KEY not found in .env")
    if not database_url:
        log.error("DATABASE_URL not found in .env")
    exit(1)

# --- Import discord sau khi đã setup log ---
import discord
from discord.ext import commands

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.voice_states = True

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    log.error("DISCORD_TOKEN not found in .env")
    exit(1)

bot = commands.Bot(command_prefix='c!', intents=intents, help_command=None)
# --- Setup event and commands
from apps import events, commands, tasks
events.setup_event(bot)
commands.setup_command(bot)

@bot.event
async def on_ready():
    log.info("Bot is ready as %s", bot.user)
    tasks.setup_task(bot)

bot.run(TOKEN)