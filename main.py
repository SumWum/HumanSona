import discord
from discord.ext import commands
from util import Bot, Handlers
import os

if "config.json" in os.listdir('./'):
    config = Handlers.JSON.read()
    token = config["token"]

def get_pre(bot, message):
    id = bot.user.id
    l = [f"<@{id}> ", f"<@!{id}> ", bot.config["prefix"]]
    return l

print("Starting...")
bot = Bot(command_prefix=get_pre, owner_ids={166630166825664512, 194861788926443520, 127972772365205505})

if __name__ == '__main__':
    bot.run(token)
