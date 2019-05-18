import json
import os
import discord
import asyncio

class Handlers:
    class JSON:
        def __init__(self, bot):
            self.bot = bot

        def read():
            with open("config.json", "r", encoding="utf8") as file:
                data = json.load(file)
            return data

        def dump(data):
            with open("config.json", "w", encoding="utf8") as file:
                    json.dump(data, file, indent=4)
