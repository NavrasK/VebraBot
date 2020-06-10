import os, discord, random
from discord.ext import commands
from dotenv import load_dotenv

import CharacterGenerator
import DiceRoll

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
    try:
        result = DiceRoll.roll(diceString)
    except Exception:
        await ctx.send("Unrecognized format")
        return
    await ctx.send(ctx.message.author.mention + ": " + result)

@bot.command()
async def newchar(ctx):
    """Returns a new vebran character template"""
    newVebran = str(CharacterGenerator.generateCharacter())
    NewCharInstructions = ("Fill in the class, traits, relationship stats, "
    "physical appearance, item / ability descriptions, and backstory.  Use this as a starting point, "
    "and feel free to tweak to your liking!")
    await ctx.send(newVebran)
    await ctx.send(NewCharInstructions)

@bot.command()
async def saymyname(ctx):
    await ctx.send("You are " + ctx.message.author.mention + " [#" + str(ctx.message.author.id) + "]")

bot.run(TOKEN)