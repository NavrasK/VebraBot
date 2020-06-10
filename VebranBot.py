import os, discord, random, pymongo
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

import CharacterGenerator
import DiceRoll

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONNECTION = os.getenv('CLUSTER_URL')

cluster = MongoClient(CONNECTION)
db = cluster["Vebra"]
collection = db["Test_Database"]

description = "Bot designed for the Vebra RPG"
bot = commands.Bot(command_prefix="//", description=description)

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "]")
    CharacterGenerator.read_names()

@bot.command()
async def roll(ctx, diceString:str):
    """Roll dice in NdN format"""
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("Unrecognized format")
        return
    await ctx.send(ctx.message.author.mention + ": " + result)

@bot.command()
async def newchar(ctx):
    """Returns a new vebran character template"""
    newVebran = str(CharacterGenerator.generateCharacter())
    NewCharInstructions = ("Fill in the class, traits, relationship stats, "
    "physical appearance, item / ability descriptions, and backstory.  Use this as a starting point, "
    "and feel free to tweak to your liking!")
    await ctx.send(newVebran)
    await ctx.send(NewCharInstructions)

@bot.command()
async def saymyname(ctx):
    await ctx.send("You are " + ctx.message.author.mention + " [#" + str(ctx.message.author.id) + "]")

@bot.command()
async def register(ctx):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        post = {"_id": ctx.message.author.id, "Name": ctx.message.author.name}
        collection.insert_one(post)
        await ctx.send("Registered!")
    else:
        await ctx.send("Already registered!")

@bot.command()
async def addfield(ctx):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        await ctx.send("User is not registered yet!")
    else:
        collection.update_one({"_id": ctx.message.author.id}, {"$set": {"SecondaryField": "I AM HERE!"}})
        await ctx.send("Field added")

@bot.command()
async def changefield(ctx):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        await ctx.send("User it not registered yet!")
    else:
        collection.update_one({"_id": ctx.message.author.id}, {"$set": {"SecondaryField": "Where did I go?"}})
        await ctx.send("Field updated")

@bot.command()
async def whoami(ctx):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        await ctx.send("User is not registered yet!")
    else:
        result = collection.find({"_id": ctx.message.author.id})
        for val in result:
            name = val["Name"]
        await ctx.send(name)

bot.run(TOKEN)