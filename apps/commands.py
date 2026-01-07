import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from . import DrawCard
import logging
import asyncio
from utils import database

import re
import string
def _clean_name(name: str) -> str:
    """
    Giữ lại:
    - Chữ cái tiếng Việt, chữ cái ASCII
    - Số
    - Khoảng trắng
    - Tất cả ký tự in trên bàn phím (string.punctuation)
    Loại bỏ emoji và ký tự đặc biệt khác.
    """
    # Tạo danh sách các ký tự được phép
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + " "
    # Thêm tiếng Việt có dấu
    viet_chars = "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵýỷỹ"
    allowed_chars += viet_chars
    # Regex: bỏ tất cả ký tự không nằm trong allowed_chars
    pattern = f"[^{re.escape(allowed_chars)}]"
    return re.sub(pattern, '', name)

log = logging.getLogger(__name__)
load_dotenv()
rc = DrawCard.RANKCARD()

def setup_command(bot : commands.Bot):
    log.info("Setup command")
    @bot.command()
    async def ping(ctx:commands.Context):
        #with ping ms
        await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")
    
    @bot.command()
    async def help(ctx:commands.Context):
        await ctx.send(
"""\
Lệnh:
c!rank: Hiển thị rank của bạn
c!scoreboard: Hiển thị top server
c!addexp <exp>: Thêm exp cho người dùng
c!kick <user>: Cho phép kick người dùng ~~không yêu cầu quyền quản lý~~.
Bot hỗ trợ việc tự động lọc người dùng không online trong thời gian dài
"""
        )
    
    @bot.command()
    async def rank(ctx:commands.Context, member = None):
        if member is None:
            member = ctx.author #type:ignore
        async with ctx.typing():
            log.info("Rank called by " + ctx.author.name)
            # out_path = rc.rank_card(
            #     username=ctx.author.name,
            #     avatar=str(ctx.author.display_avatar.url),
            #     level=10,
            #     rank=5,
            #     current_xp=720,
            #     next_level_xp=1000,
            #     custom_background=(47,49,54),
            #     xp_color=(0, 255, 127)
            # )
            if not member.id:
                await ctx.send('Không tìm thấy người dùng nây')
                return
            scoreboard = database.getScoreboard()
            line = 1
            for user in scoreboard:
                if user[0] == str(member.id):
                    break
                line += 1
            else:
                await ctx.send('Không tìm thấy người dùng nây')
                return
            user = scoreboard[line-1][1]
            out_path = rc.rank_card(
                username=member.name,
                avatar=member.display_avatar.url,
                level=user["LVL"]["LEVEL"],
                rank=line,
                current_xp=user["LVL"]["EXP"],
                next_level_xp=user["LVL"]["LEVEL_EXP"],
                custom_background=(47,49,54),
                xp_color=(0, 255, 127)
            )
            await ctx.send(file=discord.File(out_path))
    
    @bot.command()
    async def ignore(ctx:commands.Context, target : discord.Member | None = None):
        if target is None:
            member: discord.User = ctx.author #type:ignore
        else:
            member: discord.User = target #type:ignore
        mode = database.ignoreWarn(str(member.id))
        if mode:
            await ctx.send(f"Bot sẽ nhắc nhở người dùng <@{member.id}>")
        else:
            await ctx.send(f"Bot sẽ dừng nhắc nhở người dùng <@{member.id}>")
        log.info("Ignore called by " + ctx.author.name + " for " + member.name + " with mode " + str(mode))
    
    # @rank.error
    # async def rank_error(ctx:commands.Context, error):
    #     if isinstance(error, commands.BadArgument):
    #         await ctx.send('Không tìm thấy người dùng nây')
    #     else:
    #         await ctx.send('Có lỗi xảy ra. Vui lòng gọi ChaosMAX_ để khứa giải quyết')
        
    # @bot.command()
    # async def scoreboard(ctx:commands.Context):
    #     log.info("Scoreboard called by" + ctx.author.name)
    #     board = database.getScoreboard()
    #     display = f"```\n| {'RANK':<6} | {'NAME':<32} | {'LEVEL':<6} | {'EXP':<8} |\n|{'-'*8}|{'-'*34}|{'-'*8}|{'-'*10}|\n"
    #     used = False
    #     MAXLINE = 18
    #     line = 0
    #     for i, data in board.items():
    #         if i == str(ctx.author.id):
    #             used = True
    #         display += f"| {data['RANK']:<6} | {clean_name(data['DISPLAY']):<32} | {data['LEVEL']:<6} | {data['EXP']:<8} |\n" #type:ignore
    #         line += 1
    #         if line == MAXLINE:
    #             break
    #     if not used:
    #         display += f"| {'...':<6} | {'...':<32} | {'...':<6} | {'...':<8} |\n"
    #         display += f"| {board[str(ctx.author.id)]['RANK']:<6} | {_clean_name(ctx.author.display_name):<32} | {board[str(ctx.author.id)]['LEVEL']:<6} | {board[str(ctx.author.id)]['EXP']:<8} |\n"
    #     display += f"| {'...':<6} | {'...':<32} | {'...':<6} | {'...':<8} |\n"
    #     display += "```"
    #     print(display)
    #     print(len(display))
    #     await ctx.send(display)
    
    @bot.command()
    async def scoreboard(ctx:commands.Context):
        log.info("Scoreboard called by" + ctx.author.name)
        board = database.getScoreboard()
        display = f"```\n| {'RANK':<6} | {'NAME':<32} | {'LEVEL':<6} | {'EXP':<8} |\n|{'-'*8}|{'-'*34}|{'-'*8}|{'-'*10}|\n"
        line = 1
        MAX_LINE = 18
        used = False
        for id, data in board:
            userrank = line
            name = data["NAME"]
            level = data["LVL"]["LEVEL"]
            exp = data["LVL"]["TOTAL_EXP"]
            display += f"| {userrank:<6} | {name:<32} | {level:<6} | {exp:<8} |\n"
            line += 1
            if id == str(ctx.author.id):
                used = True
            if line == MAX_LINE:
                break
        line = 1
        if not used:
            display += f"| {'...':<6} | {'...':<32} | {'...':<6} | {'...':<8} |\n"
            for id, data in board:
                if id == str(ctx.author.id):
                    userrank = line
                    name = data["NAME"]
                    level = data["LVL"]["LEVEL"]
                    exp = data["LVL"]["TOTAL_EXP"]
                    display += f"| {userrank:<6} | {name:<32} | {level:<6} | {exp:<8} |\n"
                    break
                line += 1
            else:
                display += f"| {'?':<6} | {'Unknown':<32} | {'...':<6} | {'...':<8} |\n"
        display += "```"
        await ctx.send(display)
    
    @bot.command()
    async def addexp(ctx:commands.Context, exp:int):
        msg = await ctx.send("Đang thực hiện việc thêm exp cho người dùng")
        await asyncio.sleep(10)
        await msg.edit(content="Thêm 0️⃣ exp cho người dùng thành công.")
        await asyncio.sleep(3)
        await msg.edit(content="Add 0️⃣ exp cho người dùng thành công.\n:))))\nThật sự bro nghĩ rằng thg ChaosMAX_ sẽ thiết kế cái tính năng đấy à :)))")
    
    @bot.command()
    async def kick(ctx:commands.Context, user:discord.User):
        await ctx.send(f"Thg ChaosMAX_ nó lười thêm lệnh kick. :)\nĐùa thôi chứ tại Tawa có cho cấp quyền admin chó đâu.)")
        