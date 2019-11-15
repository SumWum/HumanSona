import discord
from discord.ext import commands
from util import Handlers
import asyncio

class Voice(commands.Cog, name="Voice"):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config

    @commands.Cog.listener()
    async def on_start(self):
        print("Started Voice Checker.")
        guild = self.bot.get_guild(578840384248217621)
        while True:
            for channel in guild.voice_channels:
                if channel.members:
                    for id, state in channel.voice_states.items():
                        if not state.self_mute:
                            member = guild.get_member(id)
                            if not member.bot:
                                print("yes")
                                xp = Handlers.Mongo.read()["voice_xp"][id] # Store their XP, if you want the level do the math.
                                xp += .5
                                # Consider storing the users last known level and comparing it every few seconds in this check
                                # This allows us to message them like "Hey good job! You're level X now."
                                # TODO: Work on the leaderboard
                                # TODO: Improve this code (testing, because this might fuck RAM on scale) it works but might not look pretty
            await asyncio.sleep(5)
