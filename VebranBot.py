import os, discord, random
from discord.ext import commands
from dotenv import load_dotenv
import re

import CharacterGenerator

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "Bot designed for the Vebra RPG"
bot = commands.Bot(command_prefix="//", description=description)

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " [#" + str(bot.user.id) + "]")
    CharacterGenerator.read_names()

@bot.command()
async def roll(ctx, diceString:str):
    """Roll dice in NdN format"""
    resultString = ""
    rolls = []
    try:
        dice = re.sub(r"\s", "", diceString).split("+")
        for i in range(len(dice)):
            d = dice[i]
            if re.match(r"^\d*[dD]\d*$", d):
                num, faces = map(int, d.split('d'))
                tempRolls = []
                for _ in range(num):
                    tempRolls.append(random.randint(1, faces))
                resultString += ("[" + ", ".join(tempRolls) + "]")
                rolls += tempRolls
            elif re.match(r"^\d*$", d):
                resultString += str(d)
                rolls.append(int(d))
            else:
                raise Exception("Invalid dice roll")
            if i != len(dice):
                resultString += " + "
        result = 0
        for r in rolls:
            result += r
    except Exception:
        await ctx.send("Unrecognized format")
        return
    await ctx.send("`" + diceString + " = `" + resultString + str(result))

@bot.command()
async def newchar(ctx):
    """Returns a new vebran character template"""
    newVebran = str(CharacterGenerator.generateCharacter())
    NewCharInstructions = ("Fill in the class, traits, relationship stats, "
    "physical appearance, item / ability descriptions, and backstory.  Use this as a starting point, "
    "and feel free to tweak to your liking!")
    await ctx.send(newVebran)
    await ctx.send(NewCharInstructions)

@bot.command(pass_context=True)
async def saymyname(ctx):
    await ctx.send("You are " + ctx.message.author.name + " aka " + ctx.message.author.id)

bot.run(TOKEN)