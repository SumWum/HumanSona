import discord
from discord.ext import commands
import typing
from util.handlers import Handlers

class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = Handlers.JSON.read()

    async def update_activity(self):
        activity = discord.Activity(name=f"over Furry Central",
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

    def translate(self, message: str,
        ctx: typing.Optional[commands.Context]=None,
        guild: typing.Optional[discord.Guild]=None,
        user: typing.Optional[typing.Union[discord.User, discord.Member]]=None,
        channel: typing.Optional[discord.TextChannel]=None,
        channel_2: typing.Optional[discord.TextChannel]=None,
        role: typing.Optional[discord.Role]=None,
        role_mention: typing.Optional[discord.Role]=None,
        reason: typing.Optional[str]=None):

        message = self.config["translator"][message]
        if not ctx == None:
            message = message.replace("$author", ctx.message.author.mention)
            message = message.replace("$guild", ctx.guild.name)
            message = message.replace("$channel", ctx.channel.mention)
        if not guild == None:
            message = message.replace("$guild", guild.name)
        if not user == None:
            message = message.replace("$user", user.mention)
        if not channel_2 == None:
            message = message.replace("$channel_2", channel_2.mention)
        if not channel == None:
            message = message.replace("$channel", channel.mention)
        if not role == None:
            message = message.replace("$role", role.name)
        if not role_mention == None:
            message = message.replace("$role_mention", role_mention.mention)
        if not reason == None:
            message = message.replace("$reason", reason)

        return message

    async def load_plugins(self):
        plugins = ["plugins.owner", "plugins.general", "plugins.sona", "plugins.submissions"]
        for plugin in plugins:
            self.load_extension(f"{plugin}")
            print(f"Loaded {plugin}.")
        print("Starting...")


    async def on_ready(self):
        print("Starting...")
        self.remove_command("help")
        await self.load_plugins()
        await self.update_activity()
        print(f"Logged in as {self.user} ({self.user.id})")
