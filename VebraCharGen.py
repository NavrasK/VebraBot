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
    def __str__(self):
        inv = ""
        for desc in self.inventory:
            if ("[USES: " in desc):
                inv += " ~ "
            else:
                inv += " > "
            inv += desc
            inv += "\n"
        return self.name + ", " + ("Male" if self.gender == "M" else "Female") + " " + self.race + \
            "\n Move: " + str(self.move) + "\n Power: " + str(self.power) + "\n Thought: " + str(self.thought) + \
            "\n Wonder: " + str(self.wonder) + "\n Charm: " + str(self.charm) + "\n\n" + \
            "INVENTORY\n" + "G:" + str(self.gold) + " S:" + str(self.silver) + " C:" + str(self.copper) + "\n" + inv

def readNames():
    with open("first_name_male.txt") as fnameM:
        firstNamesM = fnameM.readlines()
    with open("first_name_female.txt") as fnameF:
        firstNamesF = fnameF.readlines()  
    with open("last_name.txt") as lname:
        lastNames = lname.readlines()
    firstNamesM = [x.strip() for x in firstNamesM]
    firstNamesF = [x.strip() for x in firstNamesF]
    lastNames = [x.strip() for x in lastNames]
    return firstNamesM, firstNamesF, lastNames

def generateName(g, mfnames, ffnames, lnames):
    if (g == "M"):
        fname = mfnames[random.randrange(0, len(mfnames))]
    else:
        fname = ffnames[random.randrange(0, len(ffnames))]
    lname = lnames[random.randrange(0, len(lnames))]
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
    stats = ["Move", "Power", "Thought", "Wonder", "Charm"]
    # +1 to stat when using ability
    # Immune / resistant to x
    # x is an action using stat
    # 

def generateConsumable():
    print("TODO")
    # Heal
    # Damage
    # Temp stat boost
    # 

def generateCharacter(mf, ff, l):
    statValues = [2, 1, 0, 0, -1]
    random.shuffle(statValues)
    genders = ["M", "F"]
    gender = genders[random.randrange(0, len(genders))]
    races = {"Neka": "Move", "Golem": "Power", "Centaur": "Thought", "Human": "Wonder", "Elf": "Charm"}
    race, bonus = random.choice(list(races.items()))
    stats = {
        "Move": statValues[0],
        "Power": statValues[1],
        "Thought": statValues[2],
        "Wonder": statValues[3],
        "Charm": statValues[4]
        }
    stats[bonus] += 1
    vebran = Character(race, gender, stats["Move"], stats["Power"], stats["Thought"], stats["Wonder"], stats["Charm"])
    vebran.name = generateName(vebran.gender, mf, ff, l)
    vebran.gold, vebran.silver, vebran.copper = generateCurrency()
    for _ in range(3):
        vebran.inventory.append(generateAbility)
    for _ in range(1 + random.randint(0, 1)):
        vebran.inventory.append(generateConsumable)
    print(vebran)

# 3 random special actions / items
# 1-2 single use items
# Adventurers pack (1 bedroll, 3 days of rations, a filled waterskin, a torch, 10 feet of rope, and a tinderbox)
# random money 1-5g

# player will have to choose class, traits, relationship stats, physical appearance, and fluff / backstory

if __name__ == "__main__":
    mf, ff, l = readNames()
    generateCharacter(mf, ff, l)