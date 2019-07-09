import discord
from discord.ext import commands
from util import Handlers


class EditSona(commands.Cog, name="EditSona"):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(self.bot.config["guild"])
        self.admin_role = self.guild.get_role(self.bot.config["admin_role"])
        self.sona_edit_queue_channel = self.guild.get_channel(self.bot.config["sona_edit_queue_channel"])
        self.sona_edit_approved_channel = self.guild.get_channel(self.bot.config["sona_edit_approved_channel"])
        self.sona_edit_denied_channel = self.guild.get_channel(self.bot.config["sona_edit_denied_channel"])
        self.special_fields = ["NSFW", "Picture"]
        self.fields = {"💬": "Name",
                       "⏰": "Age",
                       "🚺": "Gender",
                       "🐹": "Species",
                       "🏳️‍🌈": "Orientation",
                       "⬆": "Height",
                       "🍔": "Weight",
                       "😀": "Bio",
                       "🍑": "Position",
                       "🖼": "Picture",
                       "🍆": "NSFW",
                       "🔴": "Color"}
        self.questions = {"Name": "Hey there! What's your fursona's name? You have 30 minutes for every question.",
                          "Gender": "What's your fursona's gender?",
                          "Age": "What's your fursona's age?",
                          "Species": "What's your fursona's species",
                          "Orientation": "What's your fursona's orientation?",
                          "Height": "What's your fursona's height?",
                          "Weight": "What's your fursona's weight?",
                          "Bio": "What's your fursona's bio?",
                          "Position": "Are Dom, Switch or Sub?",
                          "Color": "What's your favourite color? This color will be used for the embed in the sona command. (HEX only, example: #00FF7E)"}


    @commands.command()
    async def editsona(self, ctx):
        """Edits your sona."""
        data = Handlers.Mongo.read()
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

        print(str(reaction))
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
            question = "What's your fursona's picture?"
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
            question = "Is your fursona NSFW?"
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
            message = await self.sona_edit_queue_channel.send(embed=embed)
        except:
            embed.set_image(url="https://media.discordapp.net/attachments/579350335059918858/587607748653350944/Seperate_1.gif")
            message = await self.sona_edit_queue_channel.send(embed=embed)

        reactions = ["⬆", "⬇", "✅", "🚫"]
        for reaction in reactions:
            await message.add_reaction(reaction)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print("editsona")
        guild = self.bot.get_guild(self.bot.config["guild"])
        emoji = payload.emoji
        try:
            message = await (self.bot.get_channel(payload.channel_id)).fetch_message(payload.message_id)
        except:
            return
        user = guild.get_member(payload.user_id)

        if user.bot:
            return
        if not message.channel == self.sona_edit_queue_channel:
            return
        if not self.admin_role in user.roles:
            return

        embed = message.embeds[0]
        member = guild.get_member(int(embed.author.name.split(" | ")[1]))
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
            data["sonas"][str(member.id)] = answers
            Handlers.Mongo.save(data)
            print(answers)
            try:
                await member.send(self.bot.translate("APPROVED_SONA"))
            except:
                pass
            embed.color = discord.Color(0x00ce75)
            embed.set_footer(text=f"Approved by {user}.")
            await self.sona_edit_approved_channel.send(embed=embed)
            return await message.delete()

        elif str(emoji) == "🚫":
            question = await self.sona_edit_queue_channel.send(self.bot.translate("DENY_SONA", user=user))
            def check(reason):
                return self.sona_edit_queue_channel == reason.channel and user == reason.author
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
            await self.sona_edit_denied_channel.send(embed=embed)
            return await message.delete()
