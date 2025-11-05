import discord
from discord.ext import tasks, commands
from utils import database
from datetime import datetime
from zoneinfo import ZoneInfo

import logging
log = logging.getLogger(__name__)

channelID = 1389554769634398299
serverID = 760008091827306498

warnInteval = 25 #days
def setup_task(bot: commands.Bot):
    log.info("Setup task")
    @tasks.loop(minutes=1)
    async def checkVoice():
        log.info("Start check voice")
        server = bot.get_guild(serverID)
        if not server:
            log.error("Server not found")
            return
        activeUsers = set()
        knownName = []
        log.debug("Check voice channel")
        for channel in server.voice_channels:
            for member in channel.members:
                activeUsers.add(str(member.id))
                knownName.append(member.name)
        log.debug("Active users: %s", list(knownName))
        database.addVoice(list(activeUsers))
    
    @tasks.loop(minutes=10)
    async def checkUser():
        server = bot.get_guild(serverID)
        if not server:
            log.error("Server not found")
            return
        serverMember = []
        for member in server.members:
            serverMember.append((str(member.id), member.name, member.display_name))
        database.verifyDatabase(serverMember)
    
    @tasks.loop(minutes=30)
    async def warnUser():
        tz_vn = ZoneInfo("Asia/Ho_Chi_Minh")
        now_vn = datetime.now(tz_vn)
        
        if now_vn.hour != 19 and now_vn.day != 28:
            log.debug("This is not 7pm and 30th, stop auto check")
            return
        
        server = bot.get_guild(serverID)
        if not server:
            log.error("Server not found")
            return
        allUser = database.getDatabase()    
        needWarn = []
        for id, user in allUser.items():
            lastReactDelta = (datetime.now() - datetime.strptime(user["TIMELINE"]["LAST_REACT"], "%Y-%m-%d")).days
            lastRemindDelta = (datetime.now() - datetime.strptime(user["TIMELINE"]["LAST_REMINDED"], "%Y-%m-%d")).days
            if lastReactDelta >= warnInteval:
                if lastRemindDelta !=0:
                    needWarn.append((lastReactDelta, id))
        needWarn.sort(key = lambda x: x[0])
        if len(needWarn) == 0:
            log.debug("No need to warn")
            return
        channelbot = server.get_channel(channelID)
        if not channelbot:
            log.error("Channel not found")
            return
        elif not isinstance(channelbot, discord.TextChannel):
            log.error("Channel is not text channel")
            return
        warnMessage = 'Dựa theo ghi chép của bot, chúng tôi nhận thấy các thành viên trong server đã không online trong thời gian dài'
        await channelbot.send(warnMessage)
        for day, id in needWarn:
            await channelbot.send(f"<@{id}>: {day} ngày")
    
    checkVoice.start()
    checkUser.start()
    warnUser.start()