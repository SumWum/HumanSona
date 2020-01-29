import discord
from discord.ext import commands

check_messages = {
    "NSFW": "Woah there silly, You cannot use {0} in this channel because it has been marked as NSFW.",
    "donor": "Sorry sweetie, You can not use the command {0} in this channel because you are not a donor. "
             "Please consider donating to receive this.",
}

async def send_message(ctx, embed: discord.Embed = False, message: str = False, file: discord.File = False,
                       delete: int = False):
    if isinstance(ctx.channel, discord.TextChannel):
        if can_send(ctx):
            if embed and file:
                if can_embed(ctx) and can_upload(ctx):
                    return await ctx.send(embed=embed, file=file)
                return await ctx.send("Unable to send this message because I lack permission to embed links and attach files")
            elif message and file:
                if can_upload(ctx):
                    return await ctx.send(content=message, file=file)
                return await ctx.send("Unable to send this message because I lack permission to attach files.")
            elif message and embed:
                if can_embed(ctx):
                    return await ctx.send(content=message, embed=embed)
                return await ctx.send("Unable to send this message because I lack permission to embed links.")
            elif embed:
                if can_embed(ctx):
                    return await ctx.send(embed=embed)
                return await ctx.send("Unable to send this message because I lack permission to embed links.")
            elif message:
                return await ctx.send(content=message)
            elif file:
                if can_upload(ctx):
                    return await ctx.send(file=file)
        try:
            if can_react(ctx):
                await ctx.message.add_reaction("⁉️")
        except discord.Forbidden:
            return
    if isinstance(ctx.channel, discord.DMChannel):
        try:
            if embed and file:
                return await ctx.send(embed=embed, file=file)
            elif message and file:
                return await ctx.send(content=message, file=file)
            elif message and embed:
                return await ctx.send(content=message, embed=embed)
            elif embed:
                return await ctx.send(embed=embed)
            elif message:
                return await ctx.send(content=message)
            elif file:
                return await ctx.send(file=file)
        except discord.Forbidden:
            return


def check_hierarchy(ctx: commands.Context, role: discord.Role):
    return ctx.guild.me.top_role.position > role.position


def can_manage_user(
        ctx: commands.Context = None,
        user: discord.user = None,
        guild: discord.Guild = None,

):
    if ctx:
        if user.id == ctx.guild.owner.id:
            return False
        elif ctx.guild.me.top_role > user.top_role:
            return True
    if guild:
        if user.id == guild.owner.id:
            return False
        elif guild.me.top_role > user.top_role:
            return True

def can_send(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).send_messages
    if guild and channel:
        return guild.me.permissions_in(channel).send_messages

def can_react(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).add_reactions
    if guild and channel:
        return guild.me.permissions_in(channel).add_reactions

def can_embed(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).embed_links
    if guild and channel:
        return guild.me.permissions_in(channel).embed_links

def can_manage_channel(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_channels
    if guild and channel:
        return guild.me.permissions_in(channel).manage_channels

def can_external_react(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).external_emojis
    if guild and channel:
        return guild.me.permissions_in(channel).external_emojis

def can_delete(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_messages
    if guild and channel:
        return guild.me.permissions_in(channel).manage_messages

def can_kick(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).kick_members
    if guild and channel:
        return guild.me.permissions_in(channel).kick_members

def can_create_webhook(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_webhooks
    if guild and channel:
        return guild.me.permissions_in(channel).manage_webhooks

def can_upload(ctx: commands.Context, channel: discord.TextChannel = None):
    if not channel:
        channel = ctx.channel
    if not ctx.guild:
        return False
    return ctx.guild.me.permissions_in(channel).attach_files

def can_edit_role(ctx: commands.Context, role: discord.Role):
    if not ctx.guild:
        return False
    return ctx.guild.me.permissions_in(ctx.channel).manage_roles and check_hierarchy(
        ctx, role
    )
