import json
import os
import discord
import asyncio
import pymongo

client = pymongo.MongoClient("mongodb+srv://loose:loose@loose-zfcyu.mongodb.net/?retryWrites=true&w=majority")
db = client["loose-bot"]
collection = db["data"]

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

    class Mongo:
        def read():
            data = {}
            for document in collection.find():
                data[document["name"]] = document
            return data

        def create_document(name: str):
            collection.insert_one({"name": name})

        def save(data):
            for document in data:
                collection.find_and_modify(query={"name": document}, update={"$set": data[document]})

        def remove_field(name, key):
            collection.find_and_modify(query={"name": name}, update={"$unset": {key:1}})
