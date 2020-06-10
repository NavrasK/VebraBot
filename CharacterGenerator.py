import random

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
        self.name = generateName(self.gender)
        if (self.race == "Neka"):
            self.move += 1
        elif (self.race == "Golem"):
            self.power += 1
        elif (self.race == "Centaur"):
            self.thought += 1
        elif (self.race == "Human"):
            self.wonder += 1
        elif (self.race == "Elf"):
            self.charm += 1
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
        return "```\n" + self.name + ", " + ("Male" if self.gender == "M" else "Female") + " " + self.race + \
            "\n Move: " + str(self.move) + "\n Power: " + str(self.power) + "\n Thought: " + str(self.thought) + \
            "\n Wonder: " + str(self.wonder) + "\n Charm: " + str(self.charm) + "\n\n" + "INVENTORY\n" + \
            "G:" + str(self.gold) + " S:" + str(self.silver) + " C:" + str(self.copper) + "\n" + inv + "```"

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
    # Very barebones...
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
    # Not a super robust system, mostly a placeholder / for inspiration
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

def generateAdventurerGear():
    inv = []
    for _ in range(3):
        inv.append(generateAbility())
    for _ in range(1 + random.randint(0, 1)):
        inv.append(generateConsumable())
    inv += ["Rations [USES: 3]", "Bedroll", "Waterskin", "1 Torch", "10' Rope", "Tinderbox"]
    return inv

def generateCharacter():
    stats = [2, 1, 0, 0, -1]
    random.shuffle(stats)
    gender = "M" if random.randint(0, 1) == 1 else "F"
    race = random.choice(["Neka", "Golem", "Centaur", "Human", "Elf"])
    vebran = Character(race, gender, stats[0], stats[1], stats[2], stats[3], stats[4])
    vebran.gold, vebran.silver, vebran.copper = generateCurrency()
    vebran.inventory = generateAdventurerGear()
    #print(vebran)
    return vebran

if __name__ == "__main__":
    read_names()
    generateCharacter()