import random
import sys
import os

from variables import foesPerLevel, bossesPerLevel, oneTimeUseItems
from definitions import printWithPause, percentChance, greater, saveWithPickle, loadWithPickle, \
    getListOfThingsWithCommas, printInRainbowWithPause, getInput
from player import player
from foe import foe


def startGame():
    """The startGame function should initialize the game."""
    global number, room, level, pro, foes, levelFourSpawnCooldown, playerClass, canonCooldown, file, victorious
    victorious = 0
    number = 2
    room = 1
    level = 1
    pro = player()
    foes = [foe('alien soldier', 1)]
    printWithPause(3, 'Day 12')
    levelFourSpawnCooldown = 0
    playerClass = None
    canonCooldown = 3

    file = 0

    while file not in [1, 2, 3, 4]:
        try:
            print("\033[34m")
            file = int(getInput('\033[96m', 'Choose your file. Type the file number in 1-4:'))

        except ValueError:
            pass

    while playerClass not in ['police', 'soldier', 'citizen']:
        playerClass = getInput('\033[96m', "Pick your class. The choices are 'police', 'soldier', "
                                           "and 'citizen':")

    if playerClass == 'police':
        pro.maxHp = 100
        pro.inventory = ['gun', 'baton']

    elif playerClass == 'soldier':
        pro.maxHp = 100
        pro.inventory = ['knife', 'shield', 'cross', 'nunchucks', 'sacrificial dagger', 'radio', 'hissing cockroach',
                         'gas canister', 'vial of diseased blood', 'stun grenade', 'baton', 'gun', 'regen',
                         'butterfly knife']
        pro.inventory = ['knife', 'shield', 'armor', 'armor', 'sword', 'sword', 'combustible lemon']
        pro.inventory = ['knife', 'shield']
        pro.updateStats()

    elif playerClass == 'citizen':
        pro.maxHp = 150
        pro.inventory = ['regen'] * 2

    pro.hp = pro.maxHp
    pro.initialHp = pro.hp


startGame()


def addFoes():
    global number, room

    for i in range(greater(random.randint(room, room + 1), 1)):
        foes.append(foe(random.choice(foesPerLevel[level]), number))
        number += 1

    room += 1


def addBoss():
    global number, room
    room += 1
    foes.append(foe(bossesPerLevel[level], number))
    number += 1

    if level == 1:
        printWithPause(2, '\033[31m', "You found an alien commander.")
        printWithPause(2, '\033[31m', 'Kill the commander.')

    elif level == 2:
        printWithPause(2, '\033[31m', "You reached the ship's cockpit.")
        printWithPause(2, '\033[31m', "If you manage to kill the pilot, you will gain "
                       "control of the ship.")
        printWithPause(2, '\033[31m', 'Kill the pilot.')

    elif level == 3:
        printWithPause(2, '\033[31m', "You reached the room where you can regain access "
                       "to the ship's controls.")
        printWithPause(2, '\033[31m', "The room is being guarded by an alien warrior.")
        printWithPause(2, '\033[31m', "Kill the warrior.")

    room = 5


def removeFoes():
    global foes, number, victorious

    for enemy in foes:
        if enemy.hp <= 0:
            foes.remove(enemy)
            getRidOfFoe = 1

            if 'cross' in pro.inventory and not enemy.possessed and enemy.type not in ['alien commander',
                                                                                       'alien pilot', 'alien warrior',
                                                                                       'sun priest'] and enemy.hp > 10:
                if len(pro.souls) < 2:
                    if getInput('\033[96m', f"Will you take {enemy.getPrintName()}'s soul? y/n:") == 'y':
                        enemy.hp = enemy.initialHp / 2
                        enemy.attack /= 2
                        enemy.possessed = 1
                        enemy.controlledByPro = 1
                        pro.souls.append(enemy)
                        enemy.scanned = 1
                        printWithPause(0.5, '\033[96m', f"You gained {enemy.getPrintName()}'s "
                                                        f"soul, costing you {enemy.hp} hp.")
                        pro.hp -= enemy.hp
                        enemy.bleedingDamage = 0
                        enemy.poisonDamage = 0
                        enemy.stun = 0
                        getRidOfFoe = 0

                    else:
                        printWithPause(0.5, '\033[33m', f'{enemy.getPrintName()} is dead.')
                        printWithPause(0.5,'\033[96m', f"You left behind {enemy.getPrintName()}'s soul.")

                else:
                    printWithPause(0.5,'\033[96m', "You cannot hold another soul.")

            if getRidOfFoe:
                printWithPause(0.5, '\033[33m', f'{enemy.getPrintName()} is dead.')

                if level == 4:
                    pro.enemiesKilledInLevelFour += 1

                for key in enemy.loot.keys():
                    if percentChance(enemy.loot[key]):
                        if key not in oneTimeUseItems or pro.inventory.count(key) < 2:
                            pro.inventory.append(key)
                            printWithPause(0.5, '\033[96m', f'You got {key}.')

                        elif 'drone' in pro.inventory and pro.drone.inventory.count(key) == 0:
                            printWithPause(0.5, '\033[96m', f'You found {key}. You could '
                                           f'not pick it up, but your drone did. ')
                            pro.drone.inventory.append(key)

                        elif 'drone' in pro.inventory:
                            printWithPause(0.5, '\033[96m', f'You found {key}, but neither '
                                                            f'you nor your drone could pick the {key} up.')

                        else:
                            printWithPause(0.5, '\033[96m', f'You found {key}. You could not pick it up.')

                if enemy.givesPotions and percentChance(25):
                    pro.potions += 1
                    printWithPause(0.5, '\033[96m', 'You acquired a potion.')

            if enemy.type == 'alien commander':
                foes = []
                pro.potions += 5
                number = 1
                printWithPause(0.5, '\033[96m', f'You got 5 potions.')
                printWithPause(4, '\033[96m', 'You killed the alien commander. ')
                printWithPause(4, '\033[96m', 'The alien leaders, '
                               'realizing the futility of attacking the world while you live, '
                               'remove their troops.')
                printWithPause(4, '\033[96m', 'However, your victory was temporary. Once you '
                               'die, the troops will finish destroying the world.')
                printWithPause(4, '\033[96m', 'You can do more to help stop the '
                               'aliens.')
                printWithPause(4, '\033[96m', "Disguised as an alien soldier, you board a "
                               "retreating ship.")
                printWithPause(4, '\033[96m', 'Continued in chapter II...')
                pro.hasReachedLevelTwo = 1
                break

            elif enemy.type == 'alien pilot':
                foes = []
                pro.potions += 5
                number = 1
                printWithPause(0.5, '\033[96m', 'You got 5 potions.')
                printWithPause(7, '\033[96m', "Before you can finish killing the pilot, he disables "
                               "the ship's controls and alerts other pilots that "
                               "the ship is being taken over.")
                printWithPause(4, '\033[96m', 'The pilot is dead now.')
                printWithPause(4, '\033[96m', "The ship's controls must be re-enabled from "
                               "another room.")
                printWithPause(4, '\033[96m', 'Make your way to the room to gain control of your '
                               'ship.')
                printWithPause(5, '\033[96m', "The pilots that know that your ship is being hijacked "
                               "prepare to shoot your ship with their canons.")
                printWithPause(4, '\033[96m', 'Continued in chapter III...')
                break

            elif enemy.type == 'alien warrior':
                pro.potions += 25
                number = 1
                printWithPause(0.5, '\033[96m', 'You got 25 potions.')
                printWithPause(4, '\033[96m', "You killed the alien warrior.")
                printWithPause(4, '\033[96m', "You re-enable the ship's controls and make your way back "
                               "to the cockpit.")
                printWithPause(2, '\033[96m', '...',)
                printWithPause(4, '\033[96m', "Your ship is significantly quicker than the others. "
                               "You are able to escape.")
                printWithPause(2, '\033[96m', "...")
                printWithPause(4, '\033[96m', "You find the aliens' planet.")
                printWithPause(2, '\033[96m', "...")
                printWithPause(4, '\033[96m', "You have arrived.")
                printWithPause(4, '\033[96m', "Cause chaos.")
                printWithPause(4, '\033[96m', 'Continued in chapter IV...')
                pro.hasReachedLevelFour = 1
                foes = []
                break

            elif enemy.type == 'sun priest':
                while getInput('\033[96m', 'Will you proceed? y/n:') != 'y':
                    pass

                printWithPause(4, '\033[96m', 'You killed the sun priest.')
                printWithPause(4, '\033[96m', "You are victorious.")
                printWithPause(4, '\033[96m', "You sit back and wait to die, glad to have saved your planet.")
                printWithPause(4, '\033[96m', "Once you killed the priest, Earth's sun "
                               "disappeared.")
                printWithPause(2, '\033[96m', "...")
                printWithPause(4, '\033[96m', "Without the sun, Earth goes cold and dark.")
                printWithPause(4, '\033[96m', "All life on Earth's surface is gone.")
                printWithPause(6, '\033[96m', "The alien troops will never attack your "
                               "planet again.")
                printWithPause(60, '\033[96m', 'You died.')
                getInput('\033[96m', 'Press enter to proceed:')
                pro.hp = 0
                victorious = 1
                foes = []
                break


def handleCanon():
    global canonCooldown

    if level == 3 and room < 5:
        canonCooldown -= 1

        if canonCooldown <= 0:
            canonCooldown = room + 3
            pro.hp -= 40
            printWithPause(0.5, '\033[31m', f'You were hit by a canon shot, inflicting 40 damage.')

            if 'drone' in pro.inventory:
                pro.drone.hp -= 40
                printWithPause(0.5, '\033[31m', 'Your drone was hit by a canon shot, '
                                                'inflicting 40 damage.')

            for enemy in foes:
                enemy.hp -= 40
                printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} was shot by a canon, '
                                                f'inflicting 40 damage')

            removeFoes()

        else:
            printWithPause(0.5, '\033[96m', f'There are {canonCooldown} turns until you are shot by a canon.')


def addSummons():
    global foes, number

    for enemy in foes:
        for alien in enemy.newFoes:
            alien.scanned = enemy.scanned
            alien.givesPotions = 0

        foes += enemy.newFoes
        number += len(enemy.newFoes)
        enemy.newFoes = []


def handleLevelFourSpawning():
    if level == 4 and not pro.sunPriestSpawned:
        global levelFourSpawnCooldown, number

        if levelFourSpawnCooldown <= 0:
            for i in range(4):
                foes.append(foe(random.choice(foesPerLevel[4]), number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{foes[-1].getPrintName()} appeared.')
                number += 1
                levelFourSpawnCooldown = 6

        levelFourSpawnCooldown -= 1


def handleLevelFourBossSpawn():
    global foes, number
    pro.sunPriestSpawned = 1
    foes = [foe('sun priest', number, scanned=1)]
    printWithPause(5, '\033[31m', "You escaped the mob that was attacking you and fled to the cathedral.")
    printWithPause(5, '\033[31m', "Inside the cathedral, you found the priest that controls Earth's sun.")
    printWithPause(5, '\033[31m', 'Kill the priest.')
    number += 1


def saveGame():
    saveWithPickle(pro, f'playerSave{file}.pickle')
    variousData = {'level': level, 'room': room, 'foes': foes, 'number': number, 'canonCooldown': canonCooldown}
    saveWithPickle(variousData, f'variousData{file}.pickle')


def loadGame():
    try:
        global pro, level, room, foes, number, canonCooldown
        pro = loadWithPickle(f'playerSave{file}.pickle')
        variousData = loadWithPickle(f'variousData{file}.pickle')
        level = variousData['level']
        room = variousData['room']
        foes = variousData['foes']
        number = variousData['number']
        canonCooldown = variousData['canonCooldown']

        for enemy in foes:
            enemy.getUpdate()

    except FileNotFoundError:
        pass


def handleDeath():
    global number, room, foes, level
    proceed = False
    actions = ["'e' to exit the game", "'1' to start at level 1"]
    hasReachedLevelTwo = pro.hasReachedLevelTwo
    hasReachedLevelFour = pro.hasReachedLevelFour
    os.remove(f'playerSave{file}.pickle')
    os.remove(f'variousData{file}.pickle')
    startGame()
    pro.hasReachedLevelFour = hasReachedLevelFour
    pro.hasReachedLevelTwo = hasReachedLevelTwo

    if pro.hasReachedLevelTwo:
        actions.append("'2' to start at level 2")

    if pro.hasReachedLevelFour:
        actions.append("'4' to start at level 4")

    if len(actions) >= 3:
        options = getListOfThingsWithCommas('or', actions, ':', 'Type ')

    else:
        options = "Type 'e' to exit the game or '1' to start at level 1:"

    number = 1
    foes = []
    room = 0

    while not proceed:
        action = getInput('\033[96m', options)
        proceed = True

        if action == 'e':
            sys.exit()

        elif action == '1':
            level = 1
            number = 2
            foes = [foe('alien soldier', 1)]
            room = 1
            pro.potions = 3

        elif action == '2' and pro.hasReachedLevelTwo:
            level = 2
            pro.potions = 5

        elif action == '4' and pro.hasReachedLevelFour:
            level = 4
            room = 1
            pro.potions = 25

        else:
            proceed = False

        getLootForRetry(level)


def getLootForRetry(initialLevel):
    if initialLevel > 1:
        for i in range(1, initialLevel):
            foesForLoot = [foe(random.choice(foesPerLevel[i]), 1) for j in range(8)]

            for enemy in foesForLoot:
                for key in enemy.loot.keys():
                    if percentChance(enemy.loot[key]) and key not in oneTimeUseItems:
                        pro.inventory.append(key)
                        printWithPause(1, '\033[96m', f'You got {key}.')

        if initialLevel == 2:
            pro.potions = 5

        else:
            pro.potions = 25


loadGame()

while True:
    while pro.hp > 0:
        saveGame()
        removeFoes()
        printWithPause(0.5, '\033[96m', f'{level}-{room}')
        progress = pro.performNecessaryFunctions(foes, level)
        foes += pro.newFoes
        pro.newFoes = []

        if progress:
            if level == 4:
                handleLevelFourBossSpawn()

            elif room < 4:
                addFoes()

            elif room == 4:
                addBoss()

            else:
                level += 1
                room = 0
                addFoes()

            if level == 3:
                canonCooldown = room + 2
                printWithPause(0.5, '\033[96m', f'The canon must readjust its aim. You will be shot by a '
                               f'canon in {canonCooldown} turns.')

            removeFoes()

        else:
            removeFoes()
            possessedFoes = [adversary for adversary in foes if adversary.possessed]

            for enemy in foes:
                if not enemy.possessed:
                    targetList = [[pro]]

                    if possessedFoes:
                        targetList.append(possessedFoes)

                    if 'drone' in pro.inventory:
                        targetList.append([pro.drone])

                    enemy.actAsFoe(random.choice(random.choice(targetList)), number, foes, pro)

                else:
                    try:
                        otherFoes = [enemy for enemy in foes if not enemy.possessed]
                        enemy.actAsFoe(random.choice(otherFoes), number, foes, pro)

                    except IndexError:
                        pass

                addSummons()

            handleCanon()
            removeFoes()
            handleLevelFourSpawning()

    if level == 1:
        printWithPause(5, '\033[31m', 'You died. The alien troops will destroy the world.')

    elif level < 4:
        printWithPause(5, '\033[31m', 'You died. The alien troops will return. Without you, they will '
                       'have little resistance in destroying the world.')

    elif not victorious:
        printWithPause(5, '\033[31m', "Your efforts were all for nothing. The alien troops will return "
                       "to destroy the world.")

    else:
        printWithPause(5, '\033[96m', 'You won.')

    if getInput('\033[96m', f'Will you play again? y/n:') == 'y':
        for i in range(50):
            print('')

        handleDeath()

    else:
        saveGame()
        sys.exit()
