import random
import re

def roll(diceString):
    resultString = ""
    rolls = []
    dice = re.sub(r"\s", "", diceString).split("+")
    for i in range(len(dice)):
        d = str(dice[i])
        if re.match(r"^\d*[dD]\d+$", d):
            num, faces = d.split('d')
            if num == "":
                num = 1
            else:
                num = int(num)
            faces = int(faces)
            tempRolls = []
            rollString = "["
            for n in range(num):
                val = random.randint(1, faces)
                tempRolls.append(val)
                rollString += str(val)
                if n != num - 1:
                    rollString += ", "
            rollString += "]"
            resultString += rollString
            rolls += tempRolls
        elif re.match(r"^\d+$", d):
            resultString += str(d)
            rolls.append(int(d))
        else:
            raise Exception("Invalid dice roll")
        if i != len(dice) - 1:
            resultString += " + "
    result = 0
    for r in rolls:
        result += r
    display = "`" + diceString + "`: " + resultString + " = **" + str(result) + "**"
    return display

if __name__ == "__main__":
    diceString = input("Enter dice string: ")
    print(roll(diceString))