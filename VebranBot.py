import os, discord, random, re, pymongo
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
async def roll(ctx, diceString:str = ""):
    """Roll dice in NdN format"""
    if (diceString == ""):
        diceString = "2d6"
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("`Invalid roll command`")
        return
    await ctx.send(ctx.message.author.mention + ": " + result)

@bot.command()
async def generate(ctx, arg:str = ""):
    """Returns a new vebran character template"""
    if (arg == ""):
        newVebran = str(CharacterGenerator.generateCharacter())
        NewCharInstructions = ("Fill in the class, traits, relationship stats, "
        "physical appearance, item / ability descriptions, and backstory.  Use this as a starting point, "
        "and feel free to tweak to your liking!")
    elif (arg.lower() == "npc"):
        newVebran = str(CharacterGenerator.generateNPC())
        NewCharInstructions = ("Use this as a basis for a random NPC")
    else:
        ctx.send("`Invalid generate command`")
        return
    await ctx.send(newVebran)
    await ctx.send(NewCharInstructions)

@bot.command()
async def register(ctx, arg:str = ""):
    print(arg)
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        post = {"_id": ctx.message.author.id, 
            "Name": "", "Harm": 0,
            "Move": 0, "Power": 0, "Thought": 0, "Wonder": 0, "Charm": 0,
            "Gold": 0, "Silver": 0, "Copper": 0
            }
        collection.insert_one(post)
        await ctx.send("`Registered!`")
    else:
        await ctx.send("`Already registered!`")

async def check_registration(ctx):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        await ctx.send("`You're not registered yet!  Use //register first`")
        return False
    else:
        return True

async def find_value(ctx, key, castToString = False):
    queryResult = collection.find({"_id": ctx.message.author.id})
    for val in queryResult:
        result = val[key]
    if (castToString):
        result = str(result)
    else:
        result = int(result)
    return result

async def set_value(ctx, key, val):
    collection.update_one({"_id": ctx.message.author.id}, {"$set": {key, val}})

@bot.command()
async def name(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Name: " + await find_value(ctx, "Name", True))
        elif (arg == "$RESET"):
            await set_value(ctx, "Name", "")
            await ctx.send("`Name reset`")
        else:
            args = arg.split()

@bot.command()
async def harm(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Harm: " + await find_value(ctx, "Harm", True))
        else:
            args = arg.split()

@bot.command()
async def move(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Move: " + await find_value(ctx, "Move", True))
        else:
            args = arg.split()

@bot.command()
async def power(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Power: " + await find_value(ctx, "Power", True))
        else:
            args = arg.split()

@bot.command()
async def thought(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Thought: " + await find_value(ctx, "Thought", True))
        else:
            args = arg.split()

@bot.command()
async def wonder(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Wonder: " + await find_value(ctx, "Wonder", True))
        else:
            args = arg.split()

@bot.command()
async def charm(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Charm: " + await find_value(ctx, "Charm", True))
        else:
            args = arg.split()

@bot.command()
async def coins(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            pass
        else:
            pass

@bot.command()
async def gold(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Gold: " + await find_value(ctx, "Gold", True))
        else:
            args = arg.split()

@bot.command()
async def silver(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Silver: " + await find_value(ctx, "Silver", True))
        else:
            args = arg.split()

@bot.command()
async def copper(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Copper: " + await find_value(ctx, "Copper", True))
        else:
            args = arg.split()

bot.run(TOKEN)