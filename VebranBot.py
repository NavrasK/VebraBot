import os, discord, random
from discord.ext import commands
from dotenv import load_dotenv

import VebraCharGen

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "Bot designed for the Vebra RPG"
bot = commands.Bot(command_prefix="//", description=description)

class Character():
    name = ""
    inventory = []
    gold = 0
    silver = 0
    copper = 0
    def __init__(self, r, g, m, p, t, w, c):
        self.race = r
        self.gender = g
        self.move = m
        self.power = p
        self.thought = t
        self.wonder = w
        self.charm = c
    def __str__(self):
        inv = ""
        for desc in self.inventory:
            if ("[USES: " in desc):
                inv += " ~ "
            elif ("Ability" in desc):
                inv += " # "
            else:
                inv += " > "
            inv += desc
            inv += "\n"
        return self.name + ", " + ("Male" if self.gender == "M" else "Female") + " " + self.race + \
            "\n Move: " + str(self.move) + "\n Power: " + str(self.power) + "\n Thought: " + str(self.thought) + \
            "\n Wonder: " + str(self.wonder) + "\n Charm: " + str(self.charm) + "\n\n" + \
            "INVENTORY\n" + "G:" + str(self.gold) + " S:" + str(self.silver) + " C:" + str(self.copper) + "\n" + inv

def read_names():
    global firstNamesM
    global firstNamesF
    global lastNames
    with open("first_name_male.txt") as fnameM:
        firstNamesM = fnameM.readlines()
    with open("first_name_female.txt") as fnameF:
        firstNamesF = fnameF.readlines()  
    with open("last_name.txt") as lname:
        lastNames = lname.readlines()
    firstNamesM = [x.strip() for x in firstNamesM]
    firstNamesF = [x.strip() for x in firstNamesF]
    lastNames = [x.strip() for x in lastNames]

def generateName(g):
    if (g == "M"):
        fname = firstNamesM[random.randrange(0, len(firstNamesM))]
    else:
        fname = firstNamesF[random.randrange(0, len(firstNamesF))]
    lname = lastNames[random.randrange(0, len(lastNames))]
    return fname + " " + lname

def generateCurrency():
    gold = random.randint(1, 5)
    if (gold < 5):
        silver = random.randint(4, 10)
    else:
        silver = random.randint(0, 7)
    copper = random.randint(0, 10)
    return gold, silver, copper

def generateAbility():
    ability = ""
    stats = ["Move", "Power", "Thought", "Wonder", "Charm"]
    isAbility = random.randint(0, 1)
    if (isAbility == 1):
        ability += "Ability: "
        isMutation = random.randint(0, 1)
        if (isMutation == 1):
            ability += "You are able to _____, it is an action using " + random.choice(stats)
        else:
            ability += "+1 to " + random.choice(stats) + " when applicable"
    else: 
        ability += "Item: +1 to " + random.choice(stats) + " when applicable"
    return ability

def generateConsumable():
    itemType = random.randint(0, 6)
    level = random.randint(1, 3)
    stats = ["Move", "Power", "Thought", "Wonder", "Charm"]
    consumable = ""
    if (itemType == 0):
        #heal
        consumable = "Item: Heals " + str(level) + "HP [USES: " + ("3" if level == 1 else "1") + "]"
        pass
    elif (itemType == 1):
        #damage
        consumable = "Item: Deals " + ("2" if level == 3 else "1") + " damage [USES: 1]"
        pass
    elif (itemType == 2):
        #stat
        consumable = "Item: Gives +1 to " + random.choice(stats) + " [USES: " + str(level) + "]"
        pass
    elif (itemType == 3):
        #upgraded adventuring gear (flare, grapple, medkit, headlamp)
        optionsConsumable = ["Flare", "Medkit, stabilizes wounds"]
        optionsPermanent = ["Climbing kit", "Headlamp with 1 day of oil", "Hunting trap"]
        isConsumable = random.randint(0, 1)
        if (isConsumable == 1):
            consumable = "Item: " + random.choice(optionsConsumable) + " [USES: " + str(level) + "]"
        else:
            consumable = "Item: " + random.choice(optionsPermanent)
    elif (itemType == 4):
        #relationship booster
        consumable = "Item: Gives +1 Relationship [USES: " + str(level) + "]"
    elif (itemType == 5):
        #resource point generator (food, potion, herbs)
        consumable = "Item: Grants a ______ resource point [USES: " + ("4" if level == 3 else "3") + "]"
    elif (itemType == 6):
        #valuable item (gem, broken artifact, trinket)
        options = ["gem", "broken artifact", "trinket"]
        consumable = "Item: A valuable " + random.choice(options)
    return consumable

def generateCharacter():
    statValues = [2, 1, 0, 0, -1]
    random.shuffle(statValues)
    genders = ["M", "F"]
    gender = genders[random.randrange(0, len(genders))]
    races = {"Neka": "Move", "Golem": "Power", "Centaur": "Thought", "Human": "Wonder", "Elf": "Charm"}
    race, bonus = random.choice(list(races.items()))
    stats = {"Move": statValues[0], "Power": statValues[1], "Thought": statValues[2], "Wonder": statValues[3], "Charm": statValues[4]}
    stats[bonus] += 1
    vebran = Character(race, gender, stats["Move"], stats["Power"], stats["Thought"], stats["Wonder"], stats["Charm"])
    vebran.name = generateName(vebran.gender)
    vebran.gold, vebran.silver, vebran.copper = generateCurrency()
    for _ in range(3):
        vebran.inventory.append(generateAbility())
    for _ in range(1 + random.randint(0, 1)):
        vebran.inventory.append(generateConsumable())
    vebran.inventory += generateAdventurerGear()
    print(vebran)
    return vebran

def generateAdventurerGear():
    return ["Bedroll", "Rations [USES: 3]", "Waterskin", "1 Torch", "10' Rope", "Tinderbox"]

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "]")
    read_names()

@bot.command()
async def r(ctx, dice:str):
    """Roll dice in NdN format"""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send("Format must be NdN")
        return
    result = ", ".join(str(random.randint(1, limit)) for r in range (rolls))
    await ctx.send(result)

@bot.command()
async def newchar(ctx):
    """Returns a new vebran character template"""
    newVebran = str(generateCharacter())
    await ctx.send(newVebran)
    # player will have to choose class, traits, relationship stats, physical appearance, and fluff / backstory

bot.run(TOKEN)