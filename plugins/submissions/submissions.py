import discord
from discord.ext import commands
from util import Handlers


class Submissions(commands.Cog, name="Submissions"):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(self.bot.config["guild"])
        self.intro_channel = self.guild.get_channel(self.bot.config["intro_channel"])
        self.queue_channel = self.guild.get_channel(self.bot.config["queue_channel"])
        self.approved_channel = self.guild.get_channel(self.bot.config["approved_channel"])
        self.denied_channel = self.guild.get_channel(self.bot.config["denied_channel"])
        self.admin_role = self.guild.get_role(self.bot.config["admin_role"])
        self.user_role = self.guild.get_role(self.bot.config["user_role"])
        self.gatekeeper_role = self.guild.get_role(self.bot.config["gatekeeper_role"])


    @commands.command()
    async def submit(self, ctx, *, text: str=None):
        if not ctx.channel == self.intro_channel:
            return await ctx.send(self.bot.translate("FORBIDDEN_COMMAND_CHANNEL", ctx=ctx))

        embed = discord.Embed(color=discord.Color(0x7289DA))
        embed.set_author(name=f"{ctx.author} | {str(ctx.author.id)}", icon_url=ctx.author.avatar_url)
        embed.description = text
        embed.timestamp = ctx.message.created_at
        message = await self.queue_channel.send(embed=embed)

        reactions = ["⬆", "⬇", "✅", "🚫"]
        for reaction in reactions:
            await message.add_reaction(reaction)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.intro_channel:
            if self.admin_role in message.author.roles:
                return
            await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.gatekeeper_role)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if not reaction.message.channel == self.queue_channel:
            return
        if not self.admin_role in user.roles:
            return

        message = reaction.message
        embed = message.embeds[0]
        member = self.guild.get_member(int(embed.author.name.split(" | ")[1]))

        if str(reaction) == "✅":
            await member.add_roles(self.user_role)
            await member.remove_roles(self.gatekeeper_role)
            await member.send(self.bot.translate("APPROVED_APPLICATION"))
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await self.approved_channel.send(embed=embed)
            return await message.delete()

        elif str(reaction) == "🚫":
            question = await self.queue_channel.send(self.bot.translate("DENY_QUESTION", user=user))
            def check(reason):
                return self.queue_channel == reason.channel, user == reason.author
            try:
                reason = await self.bot.wait_for("message", check=check, timeout=300)
            except:
                return await question.delete()
            await question.delete()
            await reason.delete()
            embed.color = discord.Color(0xff3f3f)
            embed.set_footer(text=f"Denied by {user}.")
            embed.add_field(name="Reason", value=reason.content)
            await member.send(self.bot.translate("DENIED_APPLICATION", reason=reason.content))
            await self.denied_channel.send(embed=embed)
            return await message.delete()
