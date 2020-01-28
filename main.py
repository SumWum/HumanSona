import asyncio
import logging
import os
import platform
from datetime import timedelta

import coloredlogs
import discord
import yaml
from discord.ext.commands import AutoShardedBot

from Checks.bot_checks import can_external_react, can_send, can_react, can_embed
from Formats.formats import avatar_check

logger = logging.getLogger()


def setup_logger():
    with open("Config/logging.yml", "r") as log_config:
        config = yaml.safe_load(log_config)

    coloredlogs.install(
        level="INFO",
        logger=logger,
        fmt=config["formats"]["console"],
        datefmt=config["formats"]["datetime"],
        level_styles=config["levels"],
        field_styles=config["fields"],
    )

    return logger


async def run():
    setup_logger()
    log = logging.getLogger("bot")
    discord_log = logging.getLogger("discord")
    discord_log.setLevel(logging.INFO)
    description = "........"
    bot = Bot(
        description=description
    )
    if __name__ == "__main__":
        commands = 0
        for extension in os.listdir("Commands"):
            if extension.endswith(".py"):
                try:
                    extension = "Commands." + extension[:-3]
                    bot.load_extension(extension)
                    commands += 1
                except Exception as e:
                    log.error(
                        f"Failed to load cog {extension}\n"
                        f"Exception: {e}\n"
                        f"{e.__cause__}"
                    )
        log.info(f"[Commands Manager] - Loaded {commands} command cogs")
        handlers = 0
        for extension in os.listdir("Handlers"):
            if extension.endswith(".py"):
                try:
                    extension = "Handlers." + extension[:-3]
                    bot.load_extension(extension)
                    handlers += 1
                except Exception as e:
                    log.error(
                        f"Failed to load cog {extension}\n"
                        f"Exception: {e}\n"
                        f"{e.__cause__}"
                    )
        log.info(f"[Handler Manager] - Loaded {handlers} Handlers")
    try:
        await bot.start(os.environ["SHERI_PROD_KEY"])
    except KeyboardInterrupt:
        await bot.logout()


class Bot(AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix=".",
            status=discord.Status.online,
            case_insensitive=True,
            shard_count=1
        )
        self.primary_color = 0x007BFF
        self.info_color = 0x17A2B8
        self.success_color = 0x28A745
        self.warning_color = 0xFFC107
        self.danger_color = 0xDC3545
        log = logging.getLogger("bot")
        discord_log = logging.getLogger("discord")
        discord_log.setLevel(logging.INFO)
        self.log = log
        self.log.info(
            f"[Shard Manager] - Configuration Received. - Launching {self.shard_count} Shards"
        )

    async def on_ready(self):
        self.log.info(
            f"########################################################################\n"
            f"- I have successfully connected to discord!\n"
            f"- Bot account: {self.user}\n"
            f"- Guilds: {len(self.guilds):,}\n"
            f"- Users: {len([member for member in self.users if not member.bot]):,}\n"
            f"- Bots: {len([bot for bot in self.users if bot.bot]):,}\n"
            f"- Discord.py Version: {discord.__version__}\n"
            f"- Python Version: {platform.python_version()}\n"
            f"########################################################################"
        )
        self.log.info("I am now listening for commands/events.")

    async def on_shard_ready(self, shard_id):
        self.log.info(
            f"[Shard Primer] - Shard {shard_id} has been primed and ready to be fucked by the public."
        )

    @staticmethod
    def error_embed(error):
        embed = discord.Embed(
            color=0xDC3545,
            description="<a:bug:474000184901369856> "
                        "Error in processing command! <a:bug:474000184901369856>\n"
                        f"{error}",
        ).set_image(url="https://sheri.bot/media/command_error.png")
        embed.set_author(
            icon_url="http://myovchev.github.io/sentry-slack/images/logo32.png",
            name="Error, Logged in sentry",
            url="https://sentry.ourmainfra.me/",
        )

        embed.set_footer(
            text="Sheri Blossom, Version: v4.2",
            icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
        )
        return embed

    @staticmethod
    def format_retry_after(retry_after):
        delta = timedelta(seconds=int(round(retry_after, 0)))
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = (
                f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            )
        elif hours:
            fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
        elif minutes:
            fmt = f"{minutes} minutes and {seconds} seconds"
        else:
            fmt = f"{seconds} seconds"
        return "You can try again in " + fmt

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, discord.ext.commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            if can_external_react(ctx):
                embed = discord.Embed(color=self.color, title="<:error:451845273124208652> Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``fur{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                embed.set_author(name="Command Help", icon_url=avatar_check(self.user),
                                 url="https://sheri.bot/commands")
                embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                 text="Powered by furhost.net")
                if can_send(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("<:error:451845273124208652>")
            else:
                embed = discord.Embed(color=self.color, title="❌ Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: fur{ctx.command.name} {ctx.command.signature}")
                embed.set_thumbnail(url=avatar_check(self.user))
                embed.set_author(name="Command Help", icon_url=avatar_check(self.user),
                                 url="https://sheri.bot/commands")
                embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                 text="Powered by furhost.net")
                if can_send(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")

        elif isinstance(exception, discord.ext.commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            if can_external_react(ctx):
                embed = discord.Embed(color=self.color, title="<:error:451845273124208652> Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``fur{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                embed.set_author(name="Command Help", icon_url=avatar_check(self.user),
                                 url="https://sheri.bot/commands")
                embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                 text="Powered by furhost.net")
                if can_send(ctx) and can_embed(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("<:error:451845273124208652>")
            else:
                embed = discord.Embed(color=self.color, title="<:error:451845273124208652> Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``fur{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                embed.set_author(name="Command Help", icon_url=avatar_check(self.user),
                                 url="https://sheri.bot/commands")
                embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                 text="Powered by furhost.net")
                if can_send(ctx) and can_embed(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")

        elif isinstance(exception, discord.ext.commands.CommandNotFound):
            # self.log.error(exception)
            return

        elif isinstance(exception, discord.ext.commands.CheckFailure):
            ctx.sentry.capture_execption(exception)

        elif isinstance(exception, discord.Forbidden):
            if can_send(ctx):
                return await ctx.send(
                    "Permission error has been detected. This is not my fault but your fault.\n"
                    "In order for me to work as intended, I require the following permissions\n"
                    "```fix\n"
                    "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                    "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                    "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                    "If you are still receiving this message, Please make sure that my top role is above the roles you want me to configure."
                )
            else:
                try:
                    if can_react(ctx):
                        await ctx.message.add_reaction("❌")
                    return await ctx.author.send(
                        "Permission error has been detected. This is not my fault but your servers fault.\n"
                        "In order for me to work as intended, I require the following permissions\n"
                        "```fix\n"
                        "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                        "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                        "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                        "If you are still receiving this message, Please make sure that my top role is above the roles you want me to configure."
                    )
                except discord.Forbidden:
                    return

        elif isinstance(exception, discord.ext.commands.CommandOnCooldown):
            delta = timedelta(seconds=int(round(exception.retry_after, 0)))
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if days:
                fmt = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            elif hours:
                fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
            elif minutes:
                fmt = f"{minutes} minutes and {seconds} seconds"
            else:
                fmt = f"{seconds} seconds"
            return await ctx.send("You can try again in " + fmt)

        elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "This command is only allowed in discord servers, sorry!"
            )
        else:
            ctx.command.reset_cooldown(ctx)
            cmd = ctx.command.name
            if can_send(ctx):
                if can_external_react(ctx):
                    await ctx.send(
                        f"<a:error:474000184263573544> | **UNEXPECTED ERROR IN ``{cmd}``** | <a:error:474000184263573544>\n"
                        "I have logged the error and have alerted the team. If this error continues to persist, please reach out to us!\n"
                        "**```fix\n"
                        f"{exception}```**")
                else:
                    await ctx.send(
                        f"❌ I have encountered an error with ``{cmd}``. I have dispached my developers to fix the issue\n"
                        "If this error continues to persist, please reach out to my team!\n"
                        "**```fix\n"
                        f"{exception}```**")
            else:
                if can_react(ctx):
                    if can_external_react(ctx):
                        await ctx.message.add_reaction(":error:451845273124208652")
                    else:
                        await ctx.message.add_reaction("❌")
                try:
                    await ctx.author.send("An error has occurred.\n"
                                          f"I am unable to send messages in {ctx.channel.mention}, But I wanted to inform"
                                          f" you that I have notified my team with the "
                                          f"issue and they will work on resolving it as soon as possible.")
                except discord.Forbidden:
                    return


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
