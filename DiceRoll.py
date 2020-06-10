import random
import re

def roll(diceString):
    resultString = ""
    rolls = ""
    dice = re.sub(r"\s", "", diceString)
    dice = re.split(r"(\W)", dice)
    for i in range(len(dice)):
        token = dice[i]
        if (re.match(r"^\d*[dD]\d+$", token)):
            token = token.lower()
            num, faces = token.split("d")
            if num == "": 
                num = 1
            else: 
                num = int(num)
            faces = int(faces)
            rollString = "["
            for n in range(num):
                val = random.randint(1, faces)
                rolls += str(val)
                rollString += str(val)
                if n != num-1:
                    rollString += ", "
                    rolls += "+"
            rollString += "]"
            resultString += rollString
        elif (re.match(r"^\d+$", token)):
            resultString += str(token)
            rolls += (str(token))
            pass
        elif (re.match(r"^[+-]$", token)):
            resultString += " " + str(token) + " "
            if token == "-":
                rolls += "-"
            else:
                rolls += "+"
        else:
            raise Exception("Invalid token: " + token)
    result = eval(rolls)
    display = "`" + diceString + "`: " + resultString + " = **" + str(result) + "**"
    return display

if __name__ == "__main__":
    diceString = input("Enter dice string: ")
    print(roll(diceString))