import discord
from discord.ext import commands
import os
import time
from util import Handlers
from disputils import BotEmbedPaginator

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        member = after
        guild = member.guild
        if not self.config["guilds"][str(guild.id)]["name"] == "central":
            return
        sfw_role = guild.get_role(self.config["guilds"][str(guild.id)]["sfw_role"])
        nsfw_roles = self.config["guilds"][str(guild.id)]["nsfw_roles"]
        if sfw_role in member.roles:
            for role in nsfw_roles:
                role = member.guild.get_role(role)
                await member.remove_roles(role)

    @commands.command()
    async def ping(self, ctx):
        """Checks bot's ping."""
        b = time.monotonic()
        message = await ctx.send("Pinging...")
        await ctx.trigger_typing()
        ping = (time.monotonic() - b) * 1000
        ping = round(ping)
        await message.delete()
        return await ctx.send(f"Pong, {ping}ms")

    @commands.command()
    async def help(self, ctx):
        """Show this command."""
        embeds = []
        blacklisted_cogs = ["Owner"]

        e = discord.Embed(color=discord.Color(0xE29F6A))
        e.set_author(name="Help", icon_url=ctx.bot.user.avatar_url)
        e.description = "Welcome to the interactive help menu!\nHere you can see the commands and their uses.\n\n**To use the interactive help menu use the reactions:**\n:track_previous: To go to this menu.\n:arrow_backward: To go to the last page.\n:arrow_forward: To go to the next page.\n:track_next: To go to the last page.\n:stop_button: To stop the interactive help menu."
        embeds.append(e)

        for cog in ctx.bot.cogs:
            cog = ctx.bot.cogs[cog]
            if not cog.qualified_name in blacklisted_cogs:
                if cog.get_commands:
                    embed = discord.Embed(color=ctx.author.color)
                    embed.set_author(name=cog.qualified_name, icon_url=ctx.bot.user.avatar_url)
                    for command in list(cog.walk_commands()):
                        embed.add_field(name=command.name, value=command.help, inline=False)
                    embeds.append(embed)
        p = BotEmbedPaginator(ctx, embeds)
        await p.run()
