import time
import random
import pickle


def lesser(a, b):
    return a if a < b else b


def greater(a, b):
    return a if a > b else b


def printWithPause(message, pause=0.5):
    print(message)
    time.sleep(pause)


def percentChance(percent):
    if random.randint(1, 100) <= percent:
        return True

    else:
        return False


def getReducedDamage(damage, target):
    return damage * (1 - target.damageReduction / 100)


def getTarget(enemies, response, fromAlly=True):
    try:
        if response == 'r':
            if fromAlly:
                priorityFoes = [enemy for enemy in enemies if not enemy.possessed]

            else:
                priorityFoes = [enemy for enemy in enemies if enemy.possessed]

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
    for i in range(len(messages) - 1):
        messages[i] += ', '

    messages[-2] += f'{conjunction} '

    finalList = beginning

    for i in messages:
        finalList += i

    finalList += ending

    return finalList


def saveWithPickle(data, file):
    try:
        with open(file, 'xb') as saveData:
            pickle.dump(data, saveData)

    except FileExistsError:
        with open(file, 'wb') as saveData:
            pickle.dump(data, saveData)


def loadWithPickle(file):
    with open(file, 'rb') as data:
        return pickle.load(data)
