import discord
from discord.ext import commands
from util import Handlers
import pprint
import json

class Sona(commands.Cog, name="Sona"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.questions = {"Name": "What is your fursona's name?",
                          "Gender": "What is your fursona's gender?",
                          "Age": "What is your fursona's age?",
                          "Species": "What is your fursona's species",
                          "Orientation": "What is your fursona's sexual orientation?",
                          "Height": "What is your fursona's height in inches (eg 66 inches)?",
                          "Weight": "What is your fursona's weight in punds (eg 155lbs)?",
                          "Bio": "What is your fursona's bio, if you have one (otherwise say `None`)? You have 30 minutes to write this before it times out automatically.",
                          "Color": "What is your favourite color? (HEX only, example: #00FF7E)"}


    @commands.command()
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def sona(self, ctx, member: discord.Member=None):
        """Displays your sona.\nIf the sona is NSFW then the command must be executed in a NSFW channel"""
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
    async def setsona(self, ctx):
        """Creates a sona."""
        if not ctx.guild:
            ctx.guild = self.bot.get_guild(402412995084288000)
        data = Handlers.Mongo.read()
        if str(ctx.author.id) in data["sonas"]:
            return await ctx.send(self.bot.translate("SONA_EXISTS"))

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

        # SFW or NSFW
        question = "Is your fursona's picture or bio NSFW?"
        type = "NSFW"
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
            sfw_role = ctx.guild.get_role(self.config["guilds"][str(ctx.guild.id)]["sfw_role"])
            if sfw_role in ctx.author.roles:
                return await ctx.send(self.bot.translate("NSFW_REQUIRED"))
            answers[type] = True
        elif str(reaction) == "🚫":
            answers[type] = False
        else:
            return await ctx.send(self.bot.translate("INVALID_OPTION"))

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
        question = "Post a link of your fursona's picture or send the image, if you have one (otherwise say `None`)."
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
            message = await sona_queue_channel.send(embed=embed)
        except:
            embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
            message = await sona_queue_channel.send(embed=embed)

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
        print(member)
        if str(emoji) == "✅":
            data = Handlers.Mongo.read()
            answers = {}
            for field in embed.fields:
                answers[str(field.name)] = str(field.value)
            if answers["NSFW"] == "True":
                answers["NSFW"] = True
            else:
                answers["NSFW"] = False
            if answers["Bio"] == "None":
                answers["Bio"] = None
            if answers["Color"] == "None":
                answers["Color"] == "#00FF7E"
            data["sonas"][str(member.id)] = answers
            Handlers.Mongo.save(data)
            print(answers)
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
    async def _sona(self, ctx, member: discord.Member=None):
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
        embed.set_author(name=f"{member} ({str(member.id)})'s sona.", icon_url=ctx.author.avatar_url)
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
            embed.set_author(name=f"{member} ({str(member.id)})'s sona.", icon_url=ctx.author.avatar_url)
            embed.description = "Send the new sona value."
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
            if newsona["Bio"] == "None":
                newsona["Bio"] = None
            data["sonas"][str(member.id)] = newsona
            Handlers.Mongo.save(data)
            embed = discord.Embed(color=ctx.author.color)
            embed.set_author(name=f"{member} ({str(member.id)})'s sona.", icon_url=ctx.author.avatar_url)
            embed.description = "Successfully modified the sona."
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
            embed.set_author(name=f"{member} ({str(member.id)})'s sona.", icon_url=ctx.author.avatar_url)
            embed.description = "Successfully deleted the sona."
            return await ctx.send(embed=embed)
