import discord
from discord.ext import commands
from util import Handlers
import datetime


class Submissions(commands.Cog, name="Submissions"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        if not guild:
            return
        if not self.bot.config["guilds"][str(guild.id)]["name"] == "central":
            return

        intro_channel = guild.get_channel(self.bot.config["guilds"][str(guild.id)]["intro_channel"])
        admin_role = guild.get_role(self.bot.config["guilds"][str(guild.id)]["admin_role"])
        queue_channel = guild.get_channel(self.bot.config["guilds"][str(guild.id)]["queue_channel"])

        if message.channel == intro_channel:
            if admin_role in message.author.roles:
                return
            embed = discord.Embed(color=discord.Color(0x7289DA))
            embed.set_author(name=f"{message.author} | {str(message.author.id)}", icon_url=message.author.avatar_url)
            embed.description = str(message.content)
            embed.timestamp = message.created_at
            message2 = await queue_channel.send(embed=embed)

            reactions = ["⬆", "⬇", "✅", "🚫"]
            for reaction in reactions:
                await message2.add_reaction(reaction)

            await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if not self.bot.config["guilds"][str(guild.id)]["name"] == "central":
            return
        gatekeeper_role = guild.get_role(self.bot.config["guilds"][str(guild.id)]["gatekeeper_role"])
        await member.add_roles(gatekeeper_role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        emoji = payload.emoji
        try:
            channel = guild.get_channel(payload.channel_id)
        except:
            return
        message = await channel.fetch_message(payload.message_id)
        user = guild.get_member(payload.user_id)

        guild_config = self.bot.config["guilds"][str(guild.id)]
        if not guild_config["name"] == "central":
            return
        intro_channel = guild.get_channel(guild_config["intro_channel"])
        queue_channel = guild.get_channel(guild_config["queue_channel"])
        approved_channel = guild.get_channel(guild_config["approved_channel"])
        denied_channel = guild.get_channel(guild_config["denied_channel"])
        welcome_channel = guild.get_channel(guild_config["welcome_channel"])
        selfrole_channel = guild.get_channel(guild_config["selfrole_channel"])
        rules_channel = guild.get_channel(guild_config["rules_channel"])
        admin_role = guild.get_role(guild_config["admin_role"])
        dev_role = guild.get_role(guild_config["dev_role"])
        user_role = guild.get_role(guild_config["user_role"])
        gatekeeper_role = guild.get_role(guild_config["gatekeeper_role"])
        welcome_role = guild.get_role(guild_config["welcome_role"])

        if user.bot:
            return
        if not message.channel == queue_channel:
            return
        if not admin_role in user.roles and not dev_role in user.roles:
            return

        embed = message.embeds[0]
        member = guild.get_member(int(embed.author.name.split(" | ")[1]))

        if str(emoji) == "✅":
            print(datetime.datetime.now(), " > tick emoji")
            await member.add_roles(user_role)
            print(datetime.datetime.now(), " > gave user role")
            await member.remove_roles(gatekeeper_role)
            print(datetime.datetime.now(), " > removed gatekeeper role")
            try:
                await member.send(self.bot.translate("APPROVED_APPLICATION"))
                print(datetime.datetime.now(), " > sent dm")
            except:
                print(datetime.datetime.now(), " > failed to send dm")
                pass
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await approved_channel.send(embed=embed)
            ebed = discord.Embed(color=discord.Color(0x9370DB))
            ebed.set_thumbnail(url=member.avatar_url)
            ebed.set_author(name=self.bot.translate("WELCOME_TITLE"), icon_url=member.avatar_url)
            ebed.description = self.bot.translate("WELCOME_DESC",
                channel=selfrole_channel,
                channel_2=rules_channel)
            print(datetime.datetime.now(), " > made embed")
            await welcome_channel.send(self.bot.translate("WELCOME_MESSAGE", user=member, role_mention=welcome_role), embed=ebed)
            print(datetime.datetime.now(), " > sent msg")
            return await message.delete()

        elif str(emoji) == "🚫":
            question = await queue_channel.send(self.bot.translate("DENY_APPLICATION", user=user))
            def check(reason):
                return queue_channel == reason.channel and user == reason.author
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
            await denied_channel.send(embed=embed)
            return await message.delete()
