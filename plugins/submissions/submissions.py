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
        self.welcome_channel = self.guild.get_channel(self.bot.config["welcome_channel"])
        self.selfrole_channel = self.guild.get_channel(self.bot.config["selfrole_channel"])
        self.rules_channel = self.guild.get_channel(self.bot.config["rules_channel"])
        self.admin_role = self.guild.get_role(self.bot.config["admin_role"])
        self.user_role = self.guild.get_role(self.bot.config["user_role"])
        self.gatekeeper_role = self.guild.get_role(self.bot.config["gatekeeper_role"])
        self.welcome_role = self.guild.get_role(self.bot.config["welcome_role"])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.intro_channel:
            if self.admin_role in message.author.roles:
                return
            embed = discord.Embed(color=discord.Color(0x7289DA))
            embed.set_author(name=f"{message.author} | {str(message.author.id)}", icon_url=message.author.avatar_url)
            embed.description = str(message.content)
            embed.timestamp = message.created_at
            message2 = await self.queue_channel.send(embed=embed)

            reactions = ["⬆", "⬇", "✅", "🚫"]
            for reaction in reactions:
                await message2.add_reaction(reaction)

            await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.add_roles(self.gatekeeper_role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(self.bot.config["guild"])
        emoji = payload.emoji
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = guild.get_member(payload.user_id)

        if user.bot:
            return
        if not message.channel == self.queue_channel:
            return
        if not self.admin_role in user.roles:
            return

        embed = message.embeds[0]
        member = guild.get_member(int(embed.author.name.split(" | ")[1]))

        if str(emoji) == "✅":
            await member.add_roles(self.user_role)
            await member.remove_roles(self.gatekeeper_role)
            try:
                await member.send(self.bot.translate("APPROVED_APPLICATION"))
            except:
                pass
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await self.approved_channel.send(embed=embed)
	    embed = discord.Embed(color=discord.Color(0x9370DB))
	    embed.set_thumbnail(url=member.avatar_url)
	    embed.set_author(name=self.bot.translate("WELCOME_TITLE"), icon_url=member.avatar_url)
            embed.description = self.bot.translate("WELCOME_DESC",
                channel=self.selfrole_channel,
                channel_2=self.rules_channel)
	    await self.welcome_channel.send(self.bot.translate("wElCOME_MESSAGE", user=member, role_mention=self.welcome_role), embed=embed)
            return await message.delete()

        elif str(emoji) == "🚫":
            question = await self.queue_channel.send(self.bot.translate("DENY_APPLICATION", user=user))
            def check(reason):
                return self.queue_channel == reason.channel and user == reason.author
            try:
                reason = await self.bot.wait_for("message", check=check, timeout=300)
            except:
                return await question.delete()
            await question.delete()
            await reason.delete()
            embed.color = discord.Color(0xff3f3f)
            embed.set_footer(text=f"Denied by {user}.")
            embed.add_field(name="Reason", value=reason.content)
            try:
                await member.send(self.bot.translate("DENIED_APPLICATION", reason=reason.content))
            except:
                pass
            await self.denied_channel.send(embed=embed)
            return await message.delete()
