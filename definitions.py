import time
import random
import pickle
import pygame

from variables import textColors


def lesser(a, b):
    """Returns the smaller value of the arguments that are put in."""
    return a if a < b else b


def greater(a, b):
    """Returns the larger value of the arguments that are put in."""
    return a if a > b else b


def printWithPause(pause=0.5, *args):
    """printWithPause(X, Y) prints X and pauses the game for Y seconds if possible."""
    text = '\033[40m'

    for arg in args:
        text += f'{arg}' + '\033[40m'

    print(text)
    # print(message)
    time.sleep(pause)


def getInput(*args):
    text = '\033[40m'

    for arg in args:
        text += arg + '\033[40m'

    return input(text)


def printInRainbowWithPause(pause, message):
    """printInRainbowWithPause(X, Y) prints X in alternating colors and pauses the game for Y seconds if possible."""
    characters = []
    text = ''
    colorNumber = 0

    for i in message:
        characters.append(textColors[colorNumber])
        characters.append(i)
        colorNumber += 1

        if colorNumber >= len(textColors):
            colorNumber = 0

    for i in characters:
        text += i

    printWithPause(pause, text)


def percentChance(percent):
    """percentChance(X) has an X% chance to return true if X is an integer and 0 <= X <= 100."""

    if random.randint(1, 100) <= percent:
        return True

    else:
        return False


def getReducedDamage(damage, target):
    """getReducedDamage(X, Y) returns how much damage Y should take from something would inflict X damage to
    a target without damage reduction."""
    return damage * (1 - target.damageReduction / 100)


def getTarget(enemies, response):
    """getTarget(X, Y) tries to return  a random foe if Y is 'r'. For Y != 'r', getTarget(X, Y) tries to return a foe
    with an id number such that a string containing the id number would be equivalent to Y."""

    try:
        if response == 'r':
            priorityFoes = [enemy for enemy in enemies if not enemy.possessed]

            if priorityFoes:
                response = random.choice(priorityFoes).number

            else:
                response = random.choice(enemies).number

        for enemy in enemies:
            if str(enemy.number) == str(response):
                return enemy

    except IndexError:
        pass


def getListOfThingsWithCommas(conjunction, messages, ending='', beginning=''):
    """Adds commas, a conjunction, a beginning, and an end to a list of phrases as appropriate."""

    if len(messages) > 2:
        for i in range(len(messages) - 1):
            messages[i] += ', '

        messages[-2] += f'{conjunction} '

        finalList = beginning

        for i in messages:
            finalList += i

        finalList += ending

        return finalList

    elif len(messages) == 2:
        return f"{beginning}{messages[0]} {conjunction} {messages[1]} {ending}"

    elif len(messages) == 1:
        return f'{beginning}{messages[0]} {ending}'

    else:
        return ''


def saveWithPickle(data, file):
    """saveWithPickle(X, Y) saves X to Y if possible."""

    try:
        with open(file, 'xb') as saveData:
            pickle.dump(data, saveData)

    except FileExistsError:
        with open(file, 'wb') as saveData:
            pickle.dump(data, saveData)


def loadWithPickle(file):
    """loadWithPickle(X) returns whatever is in X if X is the name of a file that can be loaded by pickle."""

    with open(file, 'rb') as data:
        return pickle.load(data)


def play(song):
    """Plays a song with the file name that is the argument."""
    pygame.mixer.init()
    pygame.mixer.music.load(f'music/{song}')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

def getRandomItemsFromList(list, qty):
    """Returns qty random items from list without replacement."""
    selection = []

    for i in range(qty):
        nextItem = random.choice(list)
        selection.append(nextItem)
        list.remove(nextItem)

    return selection


def getChoicesOfItemsFromList(recipient, items):
    """Gives the player a choice of which of two items from items to get."""
    choices = getRandomItemsFromList(items, 2)
    choice = None

    while choice not in choices:
        choice = getInput('\033[96m', f'What will you get? You can get '
                                      f'{choices[0]} or {choices[1]}:')

    printWithPause(1, '\033[95m', f'You got {choice}.')
    recipient.inventory.append(choice)


def betterRange(a, b):
    return range(int(lesser(a, b)), int(greater(a, b)))


def sign(a):
    return 0 if a == 0 else a / abs(a)
