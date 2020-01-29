import asyncio
import logging
import os
import platform
from datetime import timedelta

import coloredlogs
import discord
import yaml
from discord.ext.commands import AutoShardedBot

from checks.bot_checks import can_external_react, can_send, can_react, can_embed
from formats.formats import avatar_check

logger = logging.getLogger()

config = None
with open("config.json", "r") as bot_config:
    config = yaml.safe_load(bot_config)

def setup_logger():
    with open("config/logging.yml", "r") as log_config:
        logconfig = yaml.safe_load(log_config)

    coloredlogs.install(
        level="INFO",
        logger=logger,
        fmt=logconfig["formats"]["console"],
        datefmt=logconfig["formats"]["datetime"],
        level_styles=logconfig["levels"],
        field_styles=logconfig["fields"],
    )

    return logger


async def run():
    setup_logger()
    log = logging.getLogger("bot")
    discord_log = logging.getLogger("discord")
    discord_log.setLevel(logging.INFO)
    description = "........"
    bot = Bot()

    if __name__ == "__main__":
        cogs = 0
        for extension in [f.replace('.py', '') for f in os.listdir("plugins") if os.path.isfile(os.path.join("plugins", f))]:
            try:
                bot.load_extension(cogs_dir + "." + extension)
                cogs += 1
            except (discord.ClientException, ModuleNotFoundError, Exception):
                log.error(
                    f"Failed to load cog {extension}\n"
                    f"Exception: {e}\n"
                    f"{e.__cause__}"
                )
        log.info(f"[Cog Manager] - Loaded {cogs} command cogs")
    try:
        await bot.start(config["token"])
    except KeyboardInterrupt:
        await bot.logout()


class Bot(AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
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
        self.config = config
        self.log.info(
            f"[Shard Manager] - Configuration Received. - Launching {self.shard_count} Shards"
        )

    async def on_ready(self):
        self.log.info("[Bot] Connected to Discord")
        await self.update_activity()
        self.log.info("[Bot] Ready. Now listening for commands/events.")

    async def on_shard_ready(self, shard_id):
        self.log.info(
            f"[Shard Primer] - Shard {shard_id} ready."
        )

    async def update_activity(self):
        activity = discord.Activity(name=f"over Furry Central",
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

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
                embed = discord.Embed(color=self.color, title="❌ Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``.{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                if can_send(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")
            else:
                embed = discord.Embed(color=self.color, title="❌ Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``.{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                if can_send(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")

        elif isinstance(exception, discord.ext.commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            if can_external_react(ctx):
                embed = discord.Embed(color=self.color, title="❌ Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``.{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
                if can_send(ctx) and can_embed(ctx):
                    return await ctx.send(embed=embed)
                else:
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")
            else:
                embed = discord.Embed(color=self.color, title="❌ Missing Argument",
                                      description=
                                      f"{exception}\n"
                                      f"Usage: ``.{ctx.command.name} {ctx.command.signature}``")
                embed.set_thumbnail(url=avatar_check(self.user))
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
                    "Permission error detected. Please notify an admin.\n"
                    "```fix\n"
                    "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                    "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                    "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```"
                )
            else:
                try:
                    if can_react(ctx):
                        await ctx.message.add_reaction("❌")
                    return await ctx.author.send(
                        "Permission error detected. Please notify an admin.\n"
                        "```fix\n"
                        "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                        "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                        "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```"
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
            return await ctx.send("Please try again in " + fmt)

        elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "This command is not allowed in messages, sorry!"
            )
        else:
            ctx.command.reset_cooldown(ctx)
            cmd = ctx.command.name
            if can_send(ctx):
                await ctx.send("Whoops! That shouldn't have happened. I've notified the Developers to this issue.") #TODO: Include Sentry ID
            else:
                if can_react(ctx):
                    await ctx.message.add_reaction("❌")
                try:
                    await ctx.author.send("Whoops! That shouldn't have happened. I've notified the Developers to this issue.") #TODO: Include Sentry ID
                except discord.Forbidden:
                    return


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
