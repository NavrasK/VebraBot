import os, discord, random, re, pymongo, uuid, json, math
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
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

playerDict = {}

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
    "Sleight Of Hand": 5,
    "Sneak": 5,
    "Social Sciences": 1,
    "Custom": 0,
    "Credit Rating": 0,
    "Mythos": 0,
    "Sanity": 99
}

rollable = list(characteristicDefaults.keys()) + list(skillDefaults.keys())
async def getStat(val):
    return process.extractOne(val, rollable)[0]

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "] > CONFIDENTIAL")

@bot.command()
async def register(ctx, arg:str = ""):
    if (arg == ""):
        if (await check_registration(ctx, True)):
            await ctx.send("`Already registered`")
        else:
            post = {"_id": ctx.message.author.id,
                "Name": "UNKNOWN",
                "Stats": json.dumps(characteristicDefaults),
                "Skills": json.dumps(skillDefaults)
                }
            collection.insert_one(post)
            await ctx.send("`Registered!`")
    elif (arg == "$DELETE"):
        if (await check_registration(ctx)):
            collection.delete_one({"_id": ctx.message.author.id})
            await ctx.send("`Registration deleted`")
    else:
        await ctx.send("`Invalid register command`")

async def check_registration(ctx, suppressOutput = False):
    if (collection.count_documents({"_id": ctx.message.author.id}) == 0):
        if (suppressOutput == False): await ctx.send("`You're not registered yet!  Use //register first`")
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
async def character(ctx, arg:str = ""):
    if (await check_registration(ctx)):
        n = await find_value(ctx, "Name", True)
        c = json.loads(await find_value(ctx, "Stats", True))
        s = json.loads(await find_value(ctx, "Skills", True))
        statBlock = f"Name: {n}\nSTR: {c['STR']}\tDEX: {c['DEX']}\tPOW: {c['POW']}\n"
        statBlock += f"CON: {c['CON']}\tAPP: {c['APP']}\tEDU: {c['EDU']}\nSIZ: {c['SIZ']}\tINT: {c['INT']}\tLUC: {c['LUC']}\n"
        skillBlock = f""
        for skill in s.keys():
            skillBlock += f"{skill}: {s[skill]}\n"
        await ctx.send("```"+statBlock+skillBlock+"```")

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
async def setval(ctx, *args:str):
    if (await check_registration(ctx)):
        pass #TODO: set / modify skills and characteristics

async def getOutcome(val, t1, t2, t5, fumble):
    if val >= fumble: outcome = "FUMBLE!" 
    elif val > t1: outcome = "FAIL"
    elif val > t2: outcome = "SUCCESS"
    elif val > t5: outcome = "HARD SUCCESS"
    elif val == 1: outcome = "CRITICAL SUCCESS!"
    else: outcome = "EXTREME SUCCESS"
    return outcome

@bot.command()
async def r(ctx, *args:str):
    if (len(args) == 0): 
        await roll(ctx, "1d100")
        return
    
    if (await check_registration(ctx)):
        advantage = 0
        mod = 0
        skill = ""
        for arg in args:
            larg = arg.lower()
            if larg == "a" or larg == "-a" or larg == "+a": advantage += 1
            elif larg == "d" or larg == "-d" or larg == "+d": advantage -= 1
            else:
                try:
                    tempmod = int(arg)
                except ValueError:
                    skill += arg
                    continue
                mod += tempmod
        skill = await getStat(skill)
        
        if skill in list(characteristicDefaults.keys()): target = int(json.loads(await find_value(ctx, "Stats", True))[skill])
        else: target = int(json.loads(await find_value(ctx, "Skills", True))[skill])
        if (target < 50): fumble = 96
        else: fumble = 100
        target += mod
        target_hard = math.ceil(target / 2)
        target_extreme = math.ceil(target / 5)
        
        results = []
        trueVal = math.inf if advantage >= 0 else -math.inf
        trueInd = 0
        for i in range(abs(advantage)+1):
            res = DiceRoll.roll("1d100", True)
            results.append(res)
            if (advantage >= 0 and res[2] < trueVal):
                trueVal = res[2]
                trueInd = i
            elif (advantage < 0 and res[2] > trueVal):
                trueVal = res[2]
                trueInd = i
        
        if (mod > 0): skillprint = skill + " +" + str(mod)
        elif (mod < 0): skillprint = skill + " -" + str(mod)
        else: skillprint = skill
        output = f"{ctx.message.author.mention} - {await find_value(ctx, 'Name', True)}: {skillprint} ({target} / {target_hard} / {target_extreme})"
        if (abs(advantage) != 0): output += f"\n`{'DIS' if advantage < 0 else ''}ADVANTAGE x {abs(advantage)}`: "
        else: output += " - "
        for i in range(len(results)):
            if i == trueInd: output += f"**{results[i][2]}**"
            else: output += f"{results[i][2]}"
            if i < len(results) - 1: output += ", "
        output += f" >> {await getOutcome(trueVal, target, target_hard, target_extreme, fumble)}"
        await ctx.send(output)

bot.run(TOKEN)