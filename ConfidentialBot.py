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
    "Art1": 5,
    "Art2": 5,
    "Art3": 5,
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
    "Language1": 1,
    "Language2": 1,
    "Language3": 1,
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
    "Skill1": 0,
    "Skill2": 0,
    "Skill3": 0,
    "Skill4": 0,
    "Credit Rating": 0,
    "Mythos": 0
}

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "] > CONFIDENTIAL")
    CharacterGenerator.read_names()

@bot.command()
async def roll(ctx, *diceStrings):
    diceString = ""
    if (len(diceStrings) == 0): 
        diceString = "1d100"
    else:
        if (diceStrings[0] in skillDefaults.keys()):
            await roll_stat()
            return
        if (re.search(r"^\d*[dD]\d+", diceStrings[0]) == None):
            diceString = "1d100"
        else:
            diceString = diceStrings[0]
            diceStrings = diceStrings[1:]
        for ds in diceStrings:
            if (re.search(r"^[-+*/]", ds) == None):
                diceString += "+"
            diceString += ds
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("`Invalid roll command`")
        return
    await ctx.send(ctx.message.author.mention + " - " + result)

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
        if (arg.split(" ", 1)[0] == "$SET"):
            try:
                val = int(arg.split(" ", 1)[1])
            except Exception:
                await ctx.send("`Invalid " + stat.lower() + " command`")
                return
            await set_value(ctx, stat, val)
        elif (arg == "$RESET"):
            await reset_value(ctx, stat)
        else:
            mod = await find_value(ctx, stat)
            arg = re.sub(r"\s*", "", arg)
            diceString="2d6" + ("-" if mod < 0 else "+") + str(abs(mod)) + \
                ("+" if (arg != "" and (arg[0] != "+" and arg[0] != "-")) else "") + arg
            try:
                result = DiceRoll.roll(diceString)
            except Exception:
                await ctx.send("`Invalid " + stat.lower() + " command`")
                return
            await ctx.send(ctx.message.author.mention + " - " + await find_value(ctx, "Name", True) + ": " + stat + "\n" + result)

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
async def move(ctx, *arg:str):
    key = "Move"
    await roll_stat(ctx, key, arg)

bot.run(TOKEN)