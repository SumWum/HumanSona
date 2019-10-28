from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import aiohttp

# to expose to the eval command
import datetime
from collections import Counter

class Owner(commands.Cog, name="Owner"):
    """Owner-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(aliases=["pfp", "picture", "avatar", "icon"])
    async def setpfp(self, ctx, url: str=None):
        if url == None:
            try:
                url = ctx.message.attachements[0]
            except:
                return await ctx.send("You have to provide an image url or attached image.")

        async with aiohttp.ClientSession() as session:
            r = await session.get(url=url)
            data = await r.read()
            await ctx.bot.user.edit(avatar=data)
            r.close()
        await ctx.send("Done!")


    @commands.command(aliases=["name", "username", "setname"])
    async def setusername(self, ctx, *, name: str=None):
        if name == None:
            return await ctx.send("You have to provide a name.")

        await ctx.bot.user.edit(username=name)
        await ctx.send("Done!")
