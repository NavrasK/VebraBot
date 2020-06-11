# VebraBot
Python project to automate tasks in a homebrew tabletop RPG.

Bot prefix: //

//register ($RESET / $DELETE)
Create an account (reset your account / delete your account)

//roll (dice string)
Format NdM + X - Y... fairly flexible but doesn't support special dice operations / types.  Default: roll 2d6

//generate (npc)
Generates a template for a player character (or an NPC)

//character
Returns the players character information all at once

//name ($RESET / $SET new name)
Returns the player characters name (or resets it / sets it to a new name)

//harm ($RESET / = X / ± X)
Displays the players harm value (or resets it / sets it / modifies it).  Note: harm is clamped between 0 and 6

//(move / power / thought / wonder / charm) (±X / $SET X / $RESET)
Rolls 2d6 + your modifier for that stat (+ the optional modifier / set the value to X / reset the value)

CREDITS
Name lists were taken from https://github.com/Kroket93/Fantasy-Name-Generator-python-script-
Bot icon made by Dimi Kazak from www.flaticon.com
NPC personalities taken from https://docs.google.com/spreadsheets/d/1ZHU7AM93ntAgMSII6doSPxJO762R6-M_w3Av1XL6I_Q/edit#gid=0