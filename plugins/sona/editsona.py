import discord
from discord.ext import commands
from util import Handlers


class EditSona(commands.Cog, name="EditSona"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.special_fields = ["NSFW", "Picture"]
        self.fields = {"💬": "Name",
                       "⏰": "Age",
                       "🚺": "Gender",
                       "🐹": "Species",
                       "🏳️‍🌈": "Orientation",
                       "⬆": "Height",
                       "🍔": "Weight",
                       "😀": "Bio",
                       "🖼": "Picture",
                       "🍆": "NSFW",
                       "🔴": "Color"}
        self.questions = {"Name": "What is your fursona's name?",
                          "Gender": "What is your fursona's gender?",
                          "Age": "What is your fursona's age?",
                          "Species": "What is your fursona's species",
                          "Orientation": "What is your fursona's sexual orientation?",
                          "Height": "What is your fursona's height in inches (eg 66 inches)?",
                          "Weight": "What is your fursona's weight in pounds (eg 155lbs)?",
                          "Bio": "What is your fursona's bio, if you have one (otherwise say `None`)? You have 30 minutes to write this before it times out automatically.",
                          "Color": "What is your favourite color? (HEX only, example: #00FF7E)"}


    @commands.command()
    async def editsona(self, ctx):
        sona_edit_queue_channel = ctx.guild.get_channel(self.config["guilds"][str(ctx.guild.id)]["sona_edit_queue_channel"])
        """Edits your sona."""
        if not ctx.guild:
            ctx.guild = self.bot.get_guild(402412995084288000)
        data = Handlers.Mongo.read()
        ctx.author = ctx.guild.get_member(ctx.author.id)
        try:
            sona = data["sonas"][str(ctx.author.id)]
        except:
            return await ctx.send(self.bot.translate("NO_SONA"))

        try:
            ctx.channel = (await ctx.author.send(self.bot.translate("SONA_EDIT"))).channel
        except:
            return await ctx.send(self.bot.translate("CLOSED_DMS"))

        def check(answer):
            return ctx.channel == answer.channel and ctx.author == answer.author
        def check2(reaction, user):
            return ctx.channel == reaction.message.channel and ctx.author == user

        try:
            embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.set_author(name="Pick a field to edit.", icon_url=ctx.author.avatar_url)
        embed.description = "**Fields**:"
        for field in self.fields:
            embed.description = f"{embed.description}\n{field} - {self.fields[field]}"
        answer = await ctx.send(embed=embed)

        for field in self.fields:
            await answer.add_reaction(field)
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check2, timeout=1800)
        except:
            return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
        field = self.fields[str(reaction)]
        for r in answer.reactions:
            await answer.remove_reaction(r, ctx.me)

        if not (str(reaction) in self.fields or str(reaction) in self.special_fields):
            return await ctx.send(self.bot.translate("INVALID_OPTION"))


        if not str(reaction) == "🍆" and not str(reaction) == "🖼":
            question = self.questions[field]
            try:
                embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
            except:
                embed = discord.Embed(color=discord.Color(0x00ff7e))
            embed.description = question
            await ctx.send(embed=embed)

            try:
                answer = await self.bot.wait_for("message", check=check, timeout=1800)
            except:
                return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))

            sona[field] = answer.content
        elif str(reaction) == "🖼":
            # Picture
            question = "Post a link of your fursona's picture or send the image, if you have one (otherwise say `None`)."
            try:
                embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
            except:
                embed = discord.Embed(color=discord.Color(0x00ff7e))
            embed.description = question
            await ctx.send(embed=embed)

            try:
                answer = await self.bot.wait_for("message", check=check, timeout=1800)
            except:
                return await ctx.send(self.bot.translate("TIMED_OUT", ctx=ctx))
            if answer.attachments == []:
                sona[field] = str(answer.content)
            else:
                sona[field] = answer.attachments[0].url

        elif str(reaction) == "🍆":
            # SFW or NSFW
            question = "Is your fursona's picture or bio NSFW?"
            try:
                embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
            except:
                embed = discord.Embed(color=discord.Color(0x00ff7e))
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
                sona[field] = True
            elif str(reaction) == "🚫":
                sona[field] = False
            else:
                return await ctx.send(self.bot.translate("INVALID_OPTION"))
        else:
            return await ctx.send(self.bot.translate("INVALID_OPTION"))

        try:
            embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.description = "Successfully edited your sona. Please wait until staff approves it."
        await ctx.send(embed=embed)

        try:
            embed = discord.Embed(color=discord.Color(int(str(sona["Color"]).replace("#", ""), 16)))
        except:
            embed = discord.Embed(color=discord.Color(0x00ff7e))
        embed.set_author(name=f"{ctx.author} | {str(ctx.author.id)}", icon_url=ctx.author.avatar_url)
        for question in sona:
            embed.add_field(name=question, value=sona[question])
        embed.set_image(url=sona["Picture"])
        embed.timestamp = ctx.message.created_at
        try:
            message = await sona_edit_queue_channel.send("<@&603372289060372500>", embed=embed)
        except:
            embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
            message = await sona_edit_queue_channel.send("<@&603372289060372500>", embed=embed)

        reactions = ["⬆", "⬇", "✅", "🚫"]
        for reaction in reactions:
            await message.add_reaction(reaction)

    @commands.command(aliases=["delsona"])
    async def deletesona(self, ctx):
        if not ctx.guild:
            ctx.guild = self.bot.get_guild(402412995084288000)
        data = Handlers.Mongo.read()
        ctx.author = ctx.guild.get_member(ctx.author.id)
        try:
            sona = data["sonas"][str(ctx.author.id)]
        except:
            return await ctx.send(self.bot.translate("NO_SONA"))

        question = "Are you sure?"
        embed = discord.Embed(color=discord.Color(0x6666ff))
        embed.description = question
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("🚫")

        def check2(reaction, user):
            return ctx.channel == reaction.message.channel and ctx.author == user

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

        Handlers.Mongo.remove_field("sonas", str(ctx.author.id))
        embed = discord.Embed(color=discord.Color(0x7289DA))
        embed.set_author(name=f"{ctx.author} ({str(ctx.author.id)})'s sona.", icon_url=ctx.author.avatar_url)
        embed.description = "Successfully deleted the sona."
        return await ctx.send(embed=embed)


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
        sona_edit_queue_channel = guild.get_channel(guild_config["sona_edit_queue_channel"])
        sona_edit_approved_channel = guild.get_channel(guild_config["sona_edit_approved_channel"])
        sona_edit_denied_channel = guild.get_channel(guild_config["sona_edit_denied_channel"])

        if user.bot:
            return
        if not message.channel == sona_edit_queue_channel:
            return
        if not admin_role in user.roles and not dev_role in user.roles:
            return

        embed = message.embeds[0]
        member = guild.get_member(int(embed.author.name.split(" | ")[-1]))
        if str(emoji) == "✅":
            data = Handlers.Mongo.read()
            answers = {}
            for field in embed.fields:
                answers[str(field.name)] = str(field.value)
            if answers["NSFW"] == "True":
                answers["NSFW"] = True
            else:
                answers["NSFW"] = False
            data["sonas"][str(member.id)] = answers
            Handlers.Mongo.save(data)
            #print(answers)
            try:
                await member.send(self.bot.translate("APPROVED_SONA"))
            except:
                pass
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await sona_edit_approved_channel.send(embed=embed)
            return await message.delete()

        elif str(emoji) == "🚫":
            question = await sona_edit_queue_channel.send(self.bot.translate("DENY_SONA", user=user))
            def check(reason):
                return sona_edit_queue_channel == reason.channel and user == reason.author
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
            await sona_edit_denied_channel.send(embed=embed)
            return await message.delete()
