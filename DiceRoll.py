import random, re

def roll(diceString, objectReturn = False):
    resultString = ""
    rolls = ""
    diceString = re.sub(r"\s*", "", diceString)
    diceString = re.sub(r"\+\+|\-\-", "+", diceString)
    diceString = re.sub(r"\-\+|\+\-", "-", diceString)
    dice = re.split(r"(\W)", diceString)
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
            if (num > 9999 or faces > 9999): return "No"
            rollString = "["
            rolls += "("
            for n in range(num):
                val = random.randint(1, faces)
                rolls += str(val)
                rollString += str(val)
                if n != num-1:
                    rollString += ", "
                    rolls += "+"
            rollString += "]"
            rolls += ")"
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
        elif (re.match(r"^[*/]$", token)):
            resultString += " " + str(token) + " "
            if token == "*":
                rolls += "*"
            else:
                rolls += "/"
        else:
            raise Exception("Invalid token: " + token)
    result = eval(rolls)
    if (objectReturn): return [diceString, resultString, int(result)]
    display = "`" + diceString + "`: " + resultString + " = **" + str(result) + "**"
    if (len(display) > 2000): display = "`" + diceString + "`: " + " = **" + str(result) + "**"
    return display

if __name__ == "__main__":
    diceString = input("Enter dice string: ")
    print(roll(diceString))