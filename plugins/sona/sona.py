import json
import pprint

import discord
from click.globals import push_context
from discord.ext import commands

from util import Handlers


class Sona(commands.Cog, name="Profile"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.questions = {"Age": "What is your age?",
                          "Location": "What is your location?",
                          "Dating Status": "What is your current dating status?",
                          "Hobbies": "What are your hobbies/interests?",
                          "Looking For": "Who/what kind of people/person are you looking for?",
                          "About": "What is you bio? You have 30 minutes to write this before it times out automatically.",
                          "Color": "What is your favourite color? (HEX only, example: #00FF7E)",
                          "DM Status": "What is your current DMs status?"}


    @commands.command()
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def profile(self, ctx, member: discord.Member=None):
        """Displays your profile.\nIf the profile is NSFW then the command must be executed in a NSFW channel"""
        data = Handlers.Mongo.read()
        if member == None:
            member = ctx.author
        try:
            sona = data["sonas"][str(member.id)]
        except:
            return await ctx.send(self.bot.translate("NO_SONA"))

        if sona["NSFW"]:
            if not ctx.channel.is_nsfw():
                return await ctx.send(self.bot.translate("FORBIDDEN_COMMAND_CHANNEL", ctx=ctx))

        await ctx.message.add_reaction("\U0001f44c")

        try:
            embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.set_author(name=f"{member} | {str(member.id)}", icon_url=member.avatar_url)
        for question in sona:
            if not question == "Color" and not question == "NSFW" and not question == "Picture":
                embed.add_field(name=question, value=sona[question])
        embed.set_image(url=sona["Picture"])
        embed.timestamp = ctx.message.created_at

        try:
            message = await ctx.send(ctx.author.mention, embed=embed)
        except:
            embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
            message = await ctx.send(ctx.author.mention, embed=embed)


    @commands.command()
    async def setprofile(self, ctx):
        """Creates a profile."""
        if not ctx.guild:
            ctx.guild = self.bot.get_guild(402412995084288000)
        data = Handlers.Mongo.read()
        ctx.author = ctx.guild.get_member(ctx.author.id)
        if str(ctx.author.id) in data["sonas"]:
            return await ctx.send(self.bot.translate("SONA_EXISTS"))

        guild_config = self.config["guilds"][str(ctx.guild.id)]
        genderrole = list(guild_config["gender"])
        orientationrole = list(guild_config["orientation"])
        personalityrole = list(guild_config["personality"])
        pingsettingsrole = list(guild_config["pingSettings"])
        relationshiprole = list(guild_config["relationship"])
        verificationrole = list(guild_config["verification"])

        for role in ctx.author.roles:
            if not role.id in genderrole:
                return await ctx.send("You are missing your Gender role, visit the <#690055478796877890> channel.")

            if not role.id in orientationrole: 
                return await ctx.send("You are missing your Orientation role, visit the <#690055478796877890> channel.")

            if not role.id in personalityrole: 
                return await ctx.send("You are missing your Personality role, visit the <#690055478796877890> channel.")

            if not role.id in pingsettingsrole: 
                return await ctx.send("You are missing your Ping Settings role, visit the <#690055478796877890> channel.")

            if not role.id in relationshiprole: 
                return await ctx.send("You are missing your Relationship role, visit the <#690055478796877890> channel.")

        try:
            ctx.channel = (await ctx.author.send(self.bot.translate("SONA_START"))).channel
        except:
            return await ctx.send(self.bot.translate("CLOSED_DMS"))

        def check(answer):
            return ctx.channel == answer.channel and ctx.author == answer.author

        def check2(reaction, user):
            return ctx.channel == reaction.message.channel and ctx.author == user

        answers = {}
        questions = self.questions

        # Verification Roles
        type = "Verification Roles"
        ver = []
        for role in ctx.author.roles:
            if role.id in verificationrole:
                ver.append('<@&%s>' % role.id)
        ver = str(ver)
        ver = ver.replace('[', '')
        ver = ver.replace(']', '')
        ver = ver.replace('\'', '')
        answers[type] = ver

        # Gender
        type = "Gender"
        ver1 = []
        for role in ctx.author.roles:
            if role.id in genderrole:
                ver1.append('<@&%s>' % role.id)
        ver1 = str(ver1)
        ver1 = ver1.replace('[', '')
        ver1 = ver1.replace(']', '')
        ver1 = ver1.replace('\'', '')
        answers[type] = ver1

        # Orientation
        type = "Orientation"
        ver2 = []
        for role in ctx.author.roles:
            if role.id in orientationrole:
                ver2.append('<@&%s>' % role.id)
        ver2 = str(ver2)
        ver2 = ver2.replace('[', '')
        ver2 = ver2.replace(']', '')
        ver2 = ver2.replace('\'', '')
        answers[type] = ver2

        # Personality
        type = "Personality"
        ver3 = []
        for role in ctx.author.roles:
            if role.id in personalityrole:
                ver3.append('<@&%s>' % role.id)
        ver3 = str(ver3)
        ver3 = ver3.replace('[', '')
        ver3 = ver3.replace(']', '')
        ver3 = ver3.replace('\'', '')
        answers[type] = ver3

        # Ping Settings
        type = "Ping Settings"
        ver4 = []
        for role in ctx.author.roles:
            if role.id in pingsettingsrole:
                ver4.append('<@&%s>' % role.id)
        ver4 = str(ver4)
        ver4 = ver4.replace('[', '')
        ver4 = ver4.replace(']', '')
        ver4 = ver4.replace('\'', '')
        answers[type] = ver4

        # Relationship
        type = "Relationship"
        ver5 = []
        for role in ctx.author.roles:
            if role.id in relationshiprole:
                ver5.append('<@&%s>' % role.id)
        ver5 = str(ver5)
        ver5 = ver5.replace('[', '')
        ver5 = ver5.replace(']', '')
        ver5 = ver5.replace('\'', '')
        answers[type] = ver5

        # SFW or NSFW
        question = "Is your fursona's picture or bio NSFW?"
        type = "NSFW"
        answers[type] = False
        # embed = discord.Embed(color=discord.Color(0x7289DA))
        # embed.description = question
        # message = await ctx.send(embed=embed)
        # await message.add_reaction("✅")
        # await message.add_reaction("🚫")

        # try:
        #     reaction, user = await self.bot.wait_for("reaction_add", check=check2, timeout=1800)
        # except:
        #     return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
        # if str(reaction) == "✅":
        #     sfw_role = ctx.guild.get_role(self.config["guilds"][str(ctx.guild.id)]["sfw_role"])
        #     if sfw_role in ctx.author.roles:
        #         return await ctx.send(self.bot.translate("NSFW_REQUIRED"))
        #     answers[type] = True
        # elif str(reaction) == "🚫":
        #     answers[type] = False
        # else:
        #     return await ctx.send(self.bot.translate("INVALID_OPTION"))

        for type in questions:
            question = questions[type]
            embed = discord.Embed(color=discord.Color(0x7289DA))
            embed.description = question
            await ctx.send(embed=embed)

            try:
                answer = await self.bot.wait_for("message", check=check, timeout=1800)
            except:
                return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
            answers[type] = str(answer.content)

        # Picture
        question = "Post a link of a picture you'd like to include with your profile or send the image. If you don't have one, say `None`."
        type = "Picture"
        embed = discord.Embed(color=discord.Color(0x7289DA))
        embed.description = question
        await ctx.send(embed=embed)

        try:
            answer = await self.bot.wait_for("message", check=check, timeout=1800)
        except:
            return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
        if answer.attachments == []:
            answers[type] = str(answer.content)
        else:
            answers[type] = answer.attachments[0].url

        await ctx.send(self.bot.translate("SUBMIT_SUCCESS"))

        try:
            embed = discord.Embed(color=discord.Color(int(str(answers["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.set_author(name=f"{ctx.author} | {str(ctx.author.id)}", icon_url=ctx.author.avatar_url)
        for question in answers:
            embed.add_field(name=question, value=answers[question])
        embed.set_image(url=answers["Picture"])
        embed.timestamp = ctx.message.created_at
        sona_queue_channel = ctx.guild.get_channel(self.config["guilds"][str(ctx.guild.id)]["sona_queue_channel"])
        try:
            message = await sona_queue_channel.send("<@&603372289060372500>", embed=embed)
        except:
            embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
            message = await sona_queue_channel.send("<@&603372289060372500>", embed=embed)

        reactions = ["⬆", "⬇", "✅", "🚫"]
        for reaction in reactions:
            await message.add_reaction(reaction)


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

        guild_config = self.config["guilds"][str(guild.id)]
        admin_role = guild.get_role(guild_config["admin_role"])
        dev_role = guild.get_role(guild_config["dev_role"])
        sona_queue_channel = guild.get_channel(guild_config["sona_queue_channel"])
        sona_approved_channel = guild.get_channel(guild_config["sona_approved_channel"])
        sona_denied_channel = guild.get_channel(guild_config["sona_denied_channel"])

        if user.bot:
            return
        if not message.channel == sona_queue_channel:
            return
        if not admin_role in user.roles and not dev_role in user.roles:
            return

        embed = message.embeds[0]
        member = guild.get_member(int(embed.author.name.split(" | ")[-1]))
        #print(member)
        if str(emoji) == "✅":
            data = Handlers.Mongo.read()
            answers = {}
            for field in embed.fields:
                answers[str(field.name)] = str(field.value)
            if answers["NSFW"] == "True":
                answers["NSFW"] = True
            else:
                answers["NSFW"] = False
            if answers["About"] == "None":
                answers["About"] = None
            if answers["Color"] == "None":
                answers["Color"] == "#00FF7E"
            data["sonas"][str(member.id)] = answers
            Handlers.Mongo.save(data)
            #print(answers)
            try:
                await member.send(self.bot.translate("APPROVED_SONA"))
            except:
                pass
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await sona_approved_channel.send(embed=embed)
            return await message.delete()

        elif str(emoji) == "🚫":
            question = await sona_queue_channel.send(self.bot.translate("DENY_SONA", user=user))
            def check(reason):
                return sona_queue_channel == reason.channel and user == reason.author
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
                await member.send(self.bot.translate("DENIED_SONA", reason=reason.content))
            except:
                pass
            await sona_denied_channel.send(embed=embed)
            return await message.delete()


    @commands.command(hidden=True)
    async def _profile(self, ctx, member: discord.Member=None):
        guild_config = self.config["guilds"][str(ctx.guild.id)]
        admin_role = ctx.guild.get_role(guild_config["admin_role"])
        dev_role = ctx.guild.get_role(guild_config["dev_role"])
        if (not admin_role in ctx.author.roles) and (not dev_role in ctx.author.roles):
            return

        if member == None:
            member = ctx.author
        data = Handlers.Mongo.read()
        if member == None:
            member = ctx.author
        try:
            sona = data["sonas"][str(member.id)]
        except:
            return await ctx.send(self.bot.translate("NO_SONA_FOUND"))

        if not ctx.channel.is_nsfw():
            return await ctx.send(self.bot.translate("FORBIDDEN_COMMAND_CHANNEL", ctx=ctx))

        def check(answer):
            return ctx.channel == answer.channel and ctx.author == answer.author
        def check2(reaction, user):
            return ctx.channel == reaction.message.channel and ctx.author == user

        options = {"🖼": "Display",
                   "📄": "Raw",
                   "✅": "Set",
                   "🚫": "Delete"}

        try:
            embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.set_author(name=f"{member} ({str(member.id)})'s profile.", icon_url=ctx.author.avatar_url)
        embed.description = "Pick an option\n**Options:**:"
        for option in options:
            embed.description = f"{embed.description}\n{option} - {options[option]}"
        answer = await ctx.send(embed=embed)

        for option in options:
            await answer.add_reaction(option)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check2, timeout=1800)
        except:
            return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
        option = options[str(reaction)]
        await answer.clear_reactions()

        if not str(reaction) in options:
            return await ctx.send(self.bot.translate("INVALID_OPTION"))

        if option == "Display":
            try:
                embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
            except:
                embed = discord.Embed(color=discord.Color(0x00ff7e))
            embed.set_author(name=f"{member} | {str(member.id)}", icon_url=member.avatar_url)
            for question in sona:
                embed.add_field(name=question, value=sona[question])
            embed.set_image(url=sona["Picture"])
            embed.timestamp = ctx.message.created_at

            try:
                message = await ctx.send(embed=embed)
            except:
                embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
                message = await ctx.send(embed=embed)

        elif option == "Raw":
            for key in sona:
                if not key == "NSFW" and not sona[key] == None:
                    sona[key] = sona[key].replace("'", "\\`").replace('"', "“")
                else:
                    sona[key] == sona[key]
            rawsona = str(sona).replace("'", '"').replace("True", "\"True\"").replace("False", "\"False\"").replace("None", "\"None\"")
            return await ctx.send(f"```json\n{rawsona}\n```")

        elif option == "Set":
            try:
                embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
            except:
                embed = discord.Embed(color=discord.Color(0x00ff7e))
            embed.set_author(name=f"{member} ({str(member.id)})'s profile.", icon_url=ctx.author.avatar_url)
            embed.description = "Send the new profile value."
            await ctx.send(embed=embed)
            try:
                answer = await self.bot.wait_for("message", check=check, timeout=1800)
            except:
                return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
            newsona = (answer.content).replace("'", '\\\`')
            newsona = json.loads(newsona)
            if newsona["NSFW"] == "True":
                newsona["NSFW"] = True
            else:
                newsona["NSFW"] = False
            if newsona["Picture"] == "None":
                newsona["Picture"] = None
            if newsona["About"] == "None":
                newsona["About"] = None
            data["sonas"][str(member.id)] = newsona
            Handlers.Mongo.save(data)
            embed = discord.Embed(color=ctx.author.color)
            embed.set_author(name=f"{member} ({str(member.id)})'s profile.", icon_url=ctx.author.avatar_url)
            embed.description = "Successfully modified the profile."
            return await ctx.send(embed=embed)

        elif option == "Delete":
            question = "Are you sure?"
            embed = discord.Embed(color=discord.Color(0x7289DA))
            embed.description = question
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("🚫")

            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check2, timeout=1800)
            except:
                return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
            if str(reaction) == "✅":
                pass
            elif str(reaction) == "🚫":
                return await ctx.send(self.bot.translate("EXIT"))
            else:
                return await ctx.send(self.bot.translate("INVALID_OPTION"))

            Handlers.Mongo.remove_field("sonas", str(member.id))
            embed = discord.Embed(color=ctx.author.color)
            embed.set_author(name=f"{member} ({str(member.id)})'s profile.", icon_url=ctx.author.avatar_url)
            embed.description = "Successfully deleted the profile."
            return await ctx.send(embed=embed)
