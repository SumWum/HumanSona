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
                                # give the user xp
                                # do math with his xp to check if he just reached a new lvl
                                # other shit
                                # Handlers.Mongo.read()["voice_leveling"]["user_id"]
                                # I'll work on the leaderboard
                                # also feel free to improve this code, it works but might not look pretty
            await asyncio.sleep(5)
