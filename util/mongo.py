import json
import os
import discord
import asyncio
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27000/")
db = client["furryguard-bot"]
collection = db["data"]

class Mongo:
    def read():
        data = {}
        for document in collection.find():
            data[document["name"]] = document
        return data
    
    def create_document(name: str):
        collection.insert_one({"name": name}   
     
    def save(data):
        for document in data:
            collection.find_and_modify(query={"name": document}, update={"$set": data[document]}    
    
    def remove_field(name, key):
        collection.find_and_modify(query={"name": name}, update={"$unset": {key:1}})

