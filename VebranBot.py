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
            "Move": 0, "Power": 0, "Thought": 0, "Wonder": 0, "Charm": 0
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

async def reset_value(ctx, key):
    if (key == "Name"):
        await set_value(ctx, key, "")
    else:
        await set_value(ctx, key, 0)
    await ctx.send("`" + key + " reset`")

async def roll_stat(ctx, stat):
    pass

@bot.command()
async def name(ctx, arg:str = ""):
    key = "Name"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Name: " + await find_value(ctx, key, True))
        elif (arg == "$RESET"):
            await reset_value(ctx, key)
        else:
            args = arg.split()
            if (len(args) == 2 and args[0] == "="):
                name = str(args[1])
                await set_value(ctx, key, name)
            else:
                await ctx.send("`Invalid name command`")
                return

@bot.command()
async def harm(ctx, arg:str = ""):
    key = "Harm"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Harm: " + await find_value(ctx, key, True) + " / 6")
        elif (arg == "$RESET"):
            await reset_value(ctx, key)
        elif (re.match(r"^\=\d+$", arg)):
            pass
        elif (re.match(r"^\+\d+$", arg)):
            pass
        elif (re.match(r"^\-\d+$", arg)):
            pass
        else:
            args = arg.split()
            if ((len(args) == 2 and re.match(r"^[=+-]$", args[0]) and args[1].is_integer()) or re.match(r"^[=+-]\d+", args[0])):
                if (args[0] == "="):
                    harm = args[1]
                elif (args[0] == "+"):
                    harm = await find_value(ctx, "Harm")
                    harm += args[1]
                elif (args[0] == "-"):
                    harm = await find_value(ctx, "Harm")
                    harm -= args[1]
                if (harm > 6): harm = 6
                if (harm < 0): harm = 0
                await set_value(ctx, "Harm", harm)
                await.ctx.send("`Harm set to " + str(harm) + "`")
            else: 
                await ctx.send("`Invalid harm command`")
                return

@bot.command()
async def move(ctx, arg:str = ""):
    key = "Move"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Move: " + await find_value(ctx, "Move", True))
        else:
            args = arg.split()

@bot.command()
async def power(ctx, arg:str = ""):
    key = "Power"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Power: " + await find_value(ctx, "Power", True))
        else:
            args = arg.split()

@bot.command()
async def thought(ctx, arg:str = ""):
    key = "Thought"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Thought: " + await find_value(ctx, "Thought", True))
        else:
            args = arg.split()

@bot.command()
async def wonder(ctx, arg:str = ""):
    key = "Wonder"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Wonder: " + await find_value(ctx, "Wonder", True))
        else:
            args = arg.split()

@bot.command()
async def charm(ctx, arg:str = ""):
    key = "Charm"
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Charm: " + await find_value(ctx, "Charm", True))
        else:
            args = arg.split()

bot.run(TOKEN)