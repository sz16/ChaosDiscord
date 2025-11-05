import discord
from discord.ext import commands
import logging

from utils import database

log = logging.getLogger(__name__)
BOT_CHANNEL = 1389554769634398299
def setup_event(bot: commands.Bot):
    log.info("Setup event")
    @bot.event
    async def on_ready():
        log.info("Bot is ready as %s", bot.user)
        
    @bot.event
    async def on_member_join(member: discord.Member):
        try:
            if member.bot:
                return
            log.info("Member join: %s", member)
            database.addNewUser(str(member.id), member.name, member.display_name)
        except Exception as e:
            log.error('Something wrong with on_member_join')
            log.error(e)
    
    @bot.event
    async def on_member_remove(member: discord.Member):
        try:
            if member.bot:
                return
            log.info("Member leave: %s", member)
            database.deleteUser(str(member.id))
        except Exception as e:
            log.error('Something wrong with on_member_remove')
            log.error(e)
    
    @bot.event
    async def on_message(message: discord.Message):
        try:
            if message.author == bot.user:
                return
            if message.channel.id == BOT_CHANNEL:
                return
            log.info("Message of %s: %s", message.author, message.content)
            database.addMessage(str(message.author.id))
        except Exception as e:
            log.error('Something wrong with on_message')
            log.error(e)
        finally:
            try:
                await bot.process_commands(message)
            except Exception as e:
                log.error('Something wrong with process_commands')
                log.error(e)
    
    @bot.event
    async def on_reaction_add(reaction : discord.Reaction, user: discord.User):
        try:
            if user.bot:
                return
            log.info("Member react: %s", user)
            database.addReaction(str(user.id))
        except Exception as e:
            log.error('Something wrong with on_reaction_add')
            log.error(e)