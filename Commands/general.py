import time

import discord
from discord.ext import commands
from disputils import BotEmbedPaginator


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

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
            if cog.qualified_name not in blacklisted_cogs:
                if cog.get_commands:
                    embed = discord.Embed(color=ctx.author.color)
                    embed.set_author(name=cog.qualified_name, icon_url=ctx.bot.user.avatar_url)
                    for command in list(cog.walk_commands()):
                        embed.add_field(name=command.name, value=command.help, inline=False)
                    embeds.append(embed)
        p = BotEmbedPaginator(ctx, embeds)
        await p.run()
