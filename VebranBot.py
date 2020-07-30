import os, discord, random, re, pymongo, uuid
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
collection = db["Player_Characters"]

description = "Bot designed for the Vebra RPG"
bot = commands.Bot(command_prefix="//", description=description)

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "]")
    CharacterGenerator.read_names()

@bot.command()
async def roll(ctx, *diceStrings):
    if (len(diceStrings) == 0): 
        diceString = ""
    else: 
        diceString = " ".join(diceStrings)
    if (diceString == ""):
        diceString = "2d6"
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("`Invalid roll command`")
        return
    await ctx.send(ctx.message.author.mention + " - " + result)

@bot.command()
async def generate(ctx, arg:str = ""):
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
    if (arg == ""):
        if (await check_registration(ctx, True)):
            await ctx.send("`Already registered`")
        else:
            post = {"_id": ctx.message.author.id, 
                "Name": "", "Harm": 0,
                "Move": 0, "Power": 0, "Thought": 0, "Wonder": 0, "Charm": 0
                }
            collection.insert_one(post)
            await ctx.send("`Registered!`")
    elif (arg == "$RESET"):
        if (await check_registration(ctx)):
            collection.delete_one({"_id": ctx.message.author.id})
            post = {"_id": ctx.message.author.id, 
                "Name": "", "Harm": 0,
                "Move": 0, "Power": 0, "Thought": 0, "Wonder": 0, "Charm": 0
                }
            collection.insert_one(post)
            await ctx.send("`Registration reset`")
    elif (arg == "$DELETE"):
        if (await check_registration(ctx)):
            collection.delete_one({"_id": ctx.message.author.id})
            await ctx.send("`Registration deleted`")
    else:
        await ctx.send("`Invalid register command`")

@bot.command()
async def character(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        n = await find_value(ctx, "Name", True)
        h = await find_value(ctx, "Harm", True)
        m = await find_value(ctx, "Move", True)
        p = await find_value(ctx, "Power", True)
        t = await find_value(ctx, "Thought", True)
        w = await find_value(ctx, "Wonder", True)
        c = await find_value(ctx, "Charm", True)
        await ctx.send("```Name: " + n + "\nHarm: " + h + " / 6\n Move: " + m + "\n Power: " + p + \
            "\n Thought: " + t + "\n Wonder: " + w + "\n Charm: " + c + "```")

async def check_registration(ctx, suppressOutput = False):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        if (suppressOutput == False):
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

async def set_value(ctx, key, val, suppressOutput = False):
    collection.update_one({"_id": ctx.message.author.id}, {"$set": {key: val}})
    if (suppressOutput == False):
        await ctx.send("`" + key + " set to " + str(val) + "`")

async def reset_value(ctx, key):
    if (key == "Name"):
        await set_value(ctx, key, "", True)
    else:
        await set_value(ctx, key, 0, True)
    await ctx.send("`" + key + " reset`")

async def roll_stat(ctx, stat, args):
    if (len(args) == 0): 
        arg = ""
    else: 
        arg = " ".join(args)
    if (await check_registration(ctx)):
        arg = arg.strip()
        if (arg == "" or re.match(r"[+-]?\s?\d+$", arg)):
            mod = await find_value(ctx, stat)
            diceString="2d6" + ("-" if mod < 0 else "+") + str(abs(mod)) + \
                ("+" if (arg != "" and ("+" not in arg and "-" not in arg)) else "") + arg
            try:
                result = DiceRoll.roll(diceString)
            except Exception:
                await ctx.send("`Invalid " + stat.lower() + " command`")
                return
            await ctx.send(ctx.message.author.mention + " - " + await find_value(ctx, "Name", True) + ": " + stat + "\n" + result)
        elif (arg == "$RESET"):
            await reset_value(ctx, stat)
        else:
            args = arg.split(" ", 1)
            if (args[0] == "$SET"):
                try:
                    val = int(args[1])
                except Exception:
                    await ctx.send("`Invalid " + stat.lower() + " command`")
                    return
                await set_value(ctx, stat, val)
            else:
                await ctx.send("`Invalid " + stat.lower() + " command`")
                return

def clamp(n, minimum, maximum):
    return (max(min(n, maximum), minimum))

@bot.command()
async def name(ctx, *args:str):
    key = "Name"
    if (len(args) == 0): 
        arg = ""
    else: 
        arg = " ".join(args)
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Name: " + await find_value(ctx, key, True))
        elif (arg == "$RESET"):
            await reset_value(ctx, key)
        else:
            args = arg.split(" ", 1)
            if (args[0] == "$SET"):
                name = str(args[1])
                await set_value(ctx, key, name)
            else:
                await ctx.send("`Invalid name command`")
                return

@bot.command()
async def harm(ctx, *args:str):
    key = "Harm"
    if (len(args) == 0): 
        arg = ""
    else: 
        arg = " ".join(args)
    arg = arg.strip()
    if (await check_registration(ctx)):
        if (arg == ""):
            await ctx.send("Harm: " + await find_value(ctx, key, True) + " / 6")
        elif (arg == "$RESET"):
            await reset_value(ctx, key)
        elif (re.match(r"^\=\s?\d+$", arg)):
            arg = arg.strip("=")
            harm = clamp(int(arg), 0, 6)
            await set_value(ctx, key, harm)
        elif (re.match(r"^\+\s?\d+$", arg)):
            arg = arg.strip("+")
            harm = await find_value(ctx, key)
            harm += int(arg)
            harm = clamp(harm, 0, 6)
            await set_value(ctx, key, harm)
        elif (re.match(r"^\-\s?\d+$", arg)):
            arg = arg.strip("-")
            harm = await find_value(ctx, key)
            harm -= int(arg)
            harm = clamp(harm, 0, 6)
            await set_value(ctx, key, harm)
        else:
            await ctx.send("`Invalid harm command`")
            return

@bot.command()
async def move(ctx, *arg:str):
    key = "Move"
    await roll_stat(ctx, key, arg)

@bot.command()
async def power(ctx, *arg:str):
    key = "Power"
    await roll_stat(ctx, key, arg)

@bot.command()
async def thought(ctx, *arg:str):
    key = "Thought"
    await roll_stat(ctx, key, arg)

@bot.command()
async def wonder(ctx, *arg:str):
    key = "Wonder"
    await roll_stat(ctx, key, arg)

@bot.command()
async def charm(ctx, *arg:str):
    key = "Charm"
    await roll_stat(ctx, key, arg)

bot.run(TOKEN)