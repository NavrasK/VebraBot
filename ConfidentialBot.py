import os, discord, random, re, pymongo, uuid, json
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
collection = db["CoC_Characters"]

description = "Bot designed for Call of Cthulhu Confidential"
bot = commands.Bot(command_prefix="//", description=description)
random.seed()

characteristicDefaults = {
    "STR": 0,
    "CON": 0,
    "SIZ": 0,
    "DEX": 0,
    "APP": 0,
    "INT": 0,
    "POW": 0,
    "EDU": 0,
    "LUC": 0
}

skillDefaults = {
    "Art": 5,
    "Athletics": 20,
    "Business": 20,
    "City Sense": 10,
    "Conspiracy": 5,
    "Dodge": 0,
    "Drive": 20,
    "Electronics": 1,
    "Fast Talk": 5,
    "Fighting": 10,
    "Firearms": 10,
    "First Aid": 25,
    "History": 20,
    "Insight": 5,
    "Internet Use": 20,
    "Intimidate": 15,
    "Language": 1,
    "Life Sciences": 1,
    "Listen": 25,
    "Mathematics": 15,
    "Mechanics": 10,
    "Media": 10,
    "Notice": 25,
    "Persuade": 25,
    "Physical Sciences": 1,
    "Pilot": 1,
    "Programming": 5,
    "Search": 25,
    "Sleight of Hand": 5,
    "Sneak": 5,
    "Social Sciences": 1,
    "Credit Rating": 0,
    "Mythos": 0,
    "Sanity": 99
}

rollable = [
    "str", "strength", 
    "con", "constitution", 
    "siz", "size", 
    "dex", "dexterity",
    "app", "appearance", 
    "int", "intelligence", "idea", 
    "pow", "power", "willpower",
    "edu", "education", "know",
    "luc", "luck",
    "art", "craft", 
    "athletics",
    "business",
    "city sense", "city", "cs",
    "conspiracy",
    "dodge",
    "drive",
    "electronics",
    "fast talk", "fast", "ft",
    "fighting", "punch", "kick",
    "firearms", "shoot",
    "first aid", "first", "heal", "fa",
    "history",
    "insight",
    "internet use", "internet", "google", "iu",
    "intimidate",
    "language", "english",
    "life sciences", "life", "ls",
    "listen",
    "mathematics", "math", 
    "mechanics",
    "media",
    "notice",
    "persuade",
    "physical sciences", "physical", "ps", 
    "pilot", 
    "programming", "code", 
    "search",
    "sleight of hand", "sleight", "soh", 
    "sneak",
    "social sciences", "social", "ss", 
    "credit rating", "credit", "cr", 
    "mythos", 
    "sanity"
]

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "] > CONFIDENTIAL")
    CharacterGenerator.read_names()

@bot.command()
async def register(ctx, arg:str = ""):
    if (arg == ""):
        if (await check_registration(ctx, True)):
            await ctx.send("`Already registered`")
        else:
            post = {"_id": ctx.message.author.id,
                "Name": "",
                "Stats": json.dumps(characteristicDefaults),
                "Skills": json.dumps(skillDefaults)
                }
            collection.insert_one(post)
            await ctx.send("`Registered!`")
    elif (arg == "$RESET"):
        if (await check_registration(ctx)):
            collection.delete_one({"_id": ctx.message.author.id})
            post = {"_id": ctx.message.author.id, 
                "Name": "",
                "Stats": json.dumps(characteristicDefaults),
                "Skills": json.dumps(skillDefaults)
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
        c = json.loads(await find_value(ctx, "Stats", True))
        s = json.loads(await find_value(ctx, "Skills", True))
        statblock = f"Name: {n}\nSTR: {c['STR']}\tDEX: {c['DEX']}\tPOW: {c['POW']}\nCON: {c['CON']}\tAPP: {c['APP']}\tEDU: {c['EDU']}\nSIZ: {c['SIZ']}\tINT: {c['INT']}\tLUC: {c['LUC']}\n"
        skillBlock = f""
        for skill in s.keys():
            skillBlock += f"{skill}: {s[skill]}\n"
        await ctx.send("```"+statblock+skillBlock+"```")

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

@bot.command()
async def roll(ctx, *args):
    diceString = ""
    if (len(args) == 0): diceString = "1d100"
    else:
        if (re.search(r"^\d*[dD]\d+", args[0]) == None): diceString = "1d100"
        else:
            diceString = args[0]
            args = args[1:]
        for ds in args:
            if (re.search(r"^[-+*/]", ds) == None): diceString += "+"
            diceString += ds
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("`Invalid roll command`")
        return
    await ctx.send(ctx.message.author.mention + " - " + result)

@bot.command()
async def r(ctx, *args:str):
    if (len(args) == 0): await roll(ctx, "1d100")
    elif (args[0] == "set"):
        pass #TODO: set or modify value
    elif (args[0] == "$AUTOFILL"):
        pass #TODO: read in special string that sets name, characteristics, and skills, adding custom skills
    elif (args[0] in rollable):
        pass #TODO: fetch value, roll, and output result (level of success, crits)
    else:
        await ctx.send("`Invalid command`")

bot.run(TOKEN)