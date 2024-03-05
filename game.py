import random
import sys
import os

from variables import foesPerLevel, bossesPerLevel, oneTimeUseItems, songsPerLevel, initialFoesPerLevel
from definitions import printWithPause, percentChance, greater, saveWithPickle, loadWithPickle, \
    getListOfThingsWithCommas, printInRainbowWithPause, getInput, lesser, play, getChoicesOfItemsFromList
from player import player
from foe import foe

print('\033[40m')

for i in range(200):
    print('')


def startGame():
    """The startGame function should initialize the game."""
    global number, room, level, pro, foes, levelFourSpawnCooldown, playerClass, canonCooldown, file, victorious
    # Once the player dies, the victorious variable is used to tell if the player has won. The number variable
    # determines what the id number of the next foe should be. If the player is in level 3, the canonCooldown variable
    # keeps track of when the canon should fire next.
    victorious = 0
    number = 2
    room = 1
    level = 1
    pro = player()
    foes = [foe('alien soldier', 1)]
    play('The War.mp3')
    printWithPause(3, 'Day 12')
    levelFourSpawnCooldown = 0
    playerClass = None
    canonCooldown = 3
    file = 0

    while file not in [1, 2, 3, 4]:
        try:
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
        pro.inventory = ['knife', 'shield']

    elif playerClass == 'citizen':
        pro.maxHp = 150
        pro.inventory = ['regen'] * 2

    pro.hp = pro.maxHp
    pro.initialHp = pro.hp


def startAfterDeath():
    """The startAfterDeath function should help start a new game."""
    global number, room, level, pro, foes, levelFourSpawnCooldown, playerClass, canonCooldown, file, victorious
    # Once the player dies, the victorious variable is used to tell if the player has won. The number variable
    # determines what the id number of the next foe should be. If the player is in level 3, the canonCooldown variable
    # keeps track of when the canon should fire next.
    victorious = 0
    pro = player()
    play('The War.mp3')
    printWithPause(3, 'Day 12')
    levelFourSpawnCooldown = 0
    playerClass = None
    canonCooldown = 3

    while playerClass not in ['police', 'soldier', 'citizen']:
        playerClass = getInput('\033[96m', "Pick your class. The choices are 'police', 'soldier', "
                                           "and 'citizen':")

    if playerClass == 'police':
        pro.maxHp = 100
        pro.inventory = ['gun', 'baton']

    elif playerClass == 'soldier':
        pro.maxHp = 100
        pro.inventory = ['knife', 'shield']

    elif playerClass == 'citizen':
        pro.maxHp = 150
        pro.inventory = ['regen'] * 2

    pro.hp = pro.maxHp
    pro.initialHp = pro.hp


def addFoes():
    """Adds foes for when the player goes to a new room that has a number of less than seven."""
    global number, room

    for i in range(greater(random.randint(room - 1, room) + initialFoesPerLevel[level], 1)):
        foeType = random.choice(foesPerLevel[level])
        foes.append(foe(foeType, number))
        number += 1

        if foeType not in pro.foesEncountered:
            pro.foesEncountered.append(foeType)

    room += 1


def showRegularRoomSwitchingText():
    """Shows text upon reaching certain rooms in level three."""

    if level == 3:
        if room == 2:
            printWithPause(3, '\033[95m', 'You begin to doubt if you should continue your attack on the'
                                          ' aliens.')

        elif room == 4:
            printWithPause(3, '\033[95m', 'But there is no going back.')

        elif room == 5:
            printWithPause(3, '\033[95m', 'And there is nothing to go back to.')


def addBoss():
    """Adds a boss as needed for levels 1-3."""
    global number, room
    room += 1
    foeType = bossesPerLevel[level]
    foes.append(foe(foeType, number))

    if foeType not in pro.foesEncountered:
        pro.foesEncountered.append(foeType)

    number += 1

    if level == 1:
        printWithPause(2, '\033[91m', "You found an alien commander.")
        printWithPause(2, '\033[91m', 'Kill the commander.')

    elif level == 2:
        play('Hyperspace.mp3')
        printWithPause(2, '\033[91m', "You reached the ship's cockpit.")
        printWithPause(2, '\033[91m', "If you manage to kill the pilot, you will gain "
                       "control of the ship.")
        printWithPause(2, '\033[91m', 'Kill the pilot.')

    elif level == 3:
        play('Certainty .mp3')
        printWithPause(2, '\033[91m', "You reached the room where you can regain access "
                       "to the ship's controls.")
        printWithPause(2, '\033[91m', "The room is being guarded by an alien warrior.")
        printWithPause(2, '\033[91m', "Kill the warrior.")


def removeFoes():
    """Handles the procedures for enemies dying."""
    global foes, number, victorious

    for enemy in foes:
        if enemy.hp <= 0:
            foes.remove(enemy)
            getRidOfFoe = 1

            if 'cross' in pro.inventory and not enemy.possessed and enemy.type not in ['alien commander',
                                                                                       'alien pilot', 'alien warrior',
                                                                                       'sun priest',
                                                                                       'helpless sun priest']:
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
                        enemy.burnDamage = 0
                        enemy.bleedingDamageFromGun = 0
                        enemy.stun = 0
                        getRidOfFoe = 0

                    else:
                        printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} is dead.')
                        printWithPause(0.5,'\033[96m', f"You left behind {enemy.getPrintName()}'s soul.")

                else:
                    printWithPause(0.5,'\033[96m', "You cannot hold another soul.")

            if getRidOfFoe:
                if enemy.type not in ['sun priest', 'helpless sun priest']:
                    printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} is dead.')

                    if level == 4:
                        pro.enemiesKilledInLevelFour += 1

                    for key in enemy.loot.keys():
                        if percentChance(enemy.loot[key]):
                            if key not in oneTimeUseItems or pro.inventory.count(key) < 2:
                                pro.inventory.append(key)
                                printWithPause(0.5, '\033[95m', f'You got {key}.')

                            elif 'drone' in pro.inventory and pro.drone.inventory.count(key) == 0:
                                printWithPause(0.5, '\033[96m', f'You found {key}. You could '
                                               f'not pick it up, but your drone did. ')
                                pro.drone.inventory.append(key)

                            elif 'drone' in pro.inventory:
                                printWithPause(0.5, '\033[96m', f'You found {key}, but neither '
                                                                f'you nor your drone could pick the {key} up.')

                            else:
                                printWithPause(0.5, '\033[96m', f'You found {key}. You '
                                                                f'could not pick it up.')

                    if enemy.givesPotions and percentChance(25):
                        pro.potions += 1
                        printWithPause(0.5, '\033[96m', 'You acquired a potion.')

            if enemy.type == 'alien commander':
                foes = []
                pro.potions += 5
                number = 1
                printWithPause(0.5, '\033[96m', f'You got 5 potions.')
                printWithPause(4, '\033[96m', 'You killed the alien commander. ')
                choices = ['regen', 'shield', 'baton', 'knife', 'gun']

                for item in [item for item in ['shield', 'baton'] if item in pro.inventory]:
                    choices.remove(item)

                getChoicesOfItemsFromList(pro, choices)
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
                choices = ['gas canister', 'radio', 'drone', 'hissing cockroach', 'vial of diseased blood', 'armor',
                           'sword']

                for item in [item for item in ['gas canister', 'radio', 'drone', 'hissing cockroach',
                                               'vial of diseased blood'] if item in pro.inventory]:
                    choices.remove(item)

                getChoicesOfItemsFromList(pro, choices)
                printWithPause(7, '\033[96m', "Before you finished killing the pilot, he disabled "
                               "the ship's controls and alerted other pilots that "
                               "the ship was being taken over.")
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
                choices = ['gas canister', 'radio', 'hissing cockroach', 'armor']

                for item in [item for item in ['gas canister', 'radio', 'hissing cockroach'] if item in pro.inventory]:
                    choices.remove(item)

                if len(choices) > 1:
                    getChoicesOfItemsFromList(pro, choices)

                else:
                    pro.inventory.append('armor')
                    printWithPause(1, '\033[95m', 'You got armor.')

                printWithPause(4, '\033[96m', "You re-enable the ship's controls and make your way back "
                               "to the cockpit.")
                printWithPause(2, '\033[96m', '...',)
                printWithPause(4, '\033[96m', "Your ship is significantly quicker than the others. "
                               "You are able to escape.")
                printWithPause(3, '\033[96m', 'You are determined to cause as much destruction as '
                                              'possible on the aliens\' planet')
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
                hp = pro.hp
                pro.hp = lesser(random.randint(1, 10), pro.hp)
                play('Extinction.mp3')
                printWithPause(5, '\033[91m', f'The sun priest hit you, inflicting {hp - pro.hp} damage.')
                printWithPause(5, '\033[95m', 'He has collapsed. He is helpless.')
                printWithPause(5, '\033[95m', 'He is begging for your mercy and promising to bring '
                                              'peace if you spare his life')
                foes = [foe('helpless sun priest',
                            1, scanned=1)]
                pro.bleedingDamage = pro.burningDamage = pro.poisonDamage = 0
                break

            elif enemy.type == 'helpless sun priest':
                while getInput('\033[96m', 'Will you proceed? y/n:') != 'y':
                    pass

                play('My song 116.mp3')
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
    """Causes the canon to fire in level three as appropriate."""
    global canonCooldown

    if level == 3 and room < 7:
        canonCooldown -= 1

        if canonCooldown <= 0:
            canonCooldown = room + 3
            pro.hp -= 40
            printWithPause(0.5, '\033[91m', f'You were hit by a canon shot, inflicting 40 damage.')

            if 'drone' in pro.inventory:
                pro.drone.hp -= 40
                printWithPause(0.5, '\033[91m', 'Your drone was hit by a canon shot, '
                                                'inflicting 40 damage.')

            for enemy in foes:
                enemy.hp -= 40
                printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} was shot by a canon, '
                                                f'inflicting 40 damage')

            removeFoes()

        else:
            printWithPause(0.5, '\033[96m', f'There are {canonCooldown} turns until you are shot by a canon.')


def addSummons(enemy):
    """Adds foes that other foes summon to the list of foes, adjusts the number variable, and resets each foe's list
    of new foes."""
    global foes, number
    foes += enemy.newFoes
    number += len(enemy.newFoes)
    pro.foesEncountered += [adversary for adversary in enemy.newFoes if adversary.type not in pro.foesEncountered]
    enemy.newFoes = []


def handleLevelFourSpawning():
    """Causes enemies to appear in level four as needed."""

    if level == 4 and not pro.sunPriestSpawned:
        global levelFourSpawnCooldown, number

        if levelFourSpawnCooldown <= 0:
            if pro.durationInLevelFour < 25:
                foeTypes = foesPerLevel[4]
                levelFourSpawnCooldown = 6

            elif pro.durationInLevelFour < 37:
                foeTypes = foesPerLevel[4] + ['alien biologist', 'alien hitman', 'alien admiral']
                levelFourSpawnCooldown = 5

            elif pro.durationInLevelFour < 49:
                foeTypes = ['alien biologist', 'alien hitman', 'alien admiral', 'alien bishop',
                            'alien mobster', 'alien devotee', 'alien mother superior']

                levelFourSpawnCooldown = 4

            elif pro.durationInLevelFour < 61:
                foeTypes = ['alien biologist', 'alien hitman', 'alien admiral', 'alien bishop',
                            'alien mobster', 'alien devotee', 'alien mother superior']

                levelFourSpawnCooldown = 3

            else:
                foeTypes = ['alien biologist', 'alien hitman', 'alien admiral', 'alien bishop',
                            'alien mobster', 'alien devotee', 'alien mother superior']

                levelFourSpawnCooldown = 3
                levelFourSpawnCooldown = 1

            for i in range(4):
                foeType = random.choice(foeTypes)
                foes.append(foe(foeType, number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{foes[-1].getPrintName()} appeared.')
                number += 1

                if foeType not in pro.foesEncountered:
                    pro.foesEncountered.append(foeType)

        levelFourSpawnCooldown -= 1


def handleLevelFourBossSpawn():
    """Makes the sun priest appear as needed."""
    global foes, number
    pro.sunPriestSpawned = 1
    foes = [foe('sun priest', number, scanned=1)]
    play('inChurch2.mp3')
    printWithPause(5, '\033[91m', "You escaped the mob that was attacking you and fled to the cathedral.")
    printWithPause(5, '\033[91m', "Inside the cathedral, you found the priest that controls Earth's sun.")
    printWithPause(5, '\033[91m', 'Kill the priest.')
    number += 1

    if 'sun priest' not in pro.foesEncountered:
        pro.foesEncountered.append('sun priest')


def saveGame():
    """Saves the game."""
    saveWithPickle(pro, f'playerSave{file}.pickle')
    variousData = {'level': level, 'room': room, 'foes': foes, 'number': number, 'canonCooldown': canonCooldown}
    saveWithPickle(variousData, f'variousData{file}.pickle')


def loadGame():
    """Tries to load the player's file."""

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

        play(songsPerLevel[level])

    except FileNotFoundError:
        pass


def handleDeath():
    """Handles the procedure for exiting the game or starting another game upon the player's death. 😭"""
    global number, room, foes, level
    proceed = False
    actions = ["'e' to exit the game", "'1' to start at level 1"]
    hasReachedLevelTwo = pro.hasReachedLevelTwo
    hasReachedLevelFour = pro.hasReachedLevelFour
    foesEncountered = pro.foesEncountered
    startAfterDeath()
    pro.hasReachedLevelFour = hasReachedLevelFour
    pro.hasReachedLevelTwo = hasReachedLevelTwo
    pro.foesEncountered = foesEncountered

    if pro.hasReachedLevelTwo:
        actions.append("'2' to start at level 2")

    if pro.hasReachedLevelFour:
        actions.append("'4' to start at level 4")

    options = getListOfThingsWithCommas('or', actions, ':', 'Type ')
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

    saveGame()


def getCustomInput():
    """Gets player input until 'y' is entered in. Tries to execute each response from the getCustomInput function."""
    action = getInput('\033[96m', "What will you do? Type 'y' to exit the terminal for custom inputs:")

    if action != 'y':
        try:
            exec(action)

        except Exception as error:
            printWithPause(0.5, '\033[91m', f'Your command raised an error saying, "{error}."')

        getCustomInput()


def getLootForRetry(initialLevel):
    """Gives the player items based on what level the player starts a game in."""

    if initialLevel > 1:
        for i in range(1, initialLevel):
            foesForLoot = [foe(random.choice(foesPerLevel[i]), 1) for j in range(8)]

            for enemy in foesForLoot:
                for key in enemy.loot.keys():
                    if percentChance(enemy.loot[key]) and key not in oneTimeUseItems:
                        pro.inventory.append(key)
                        printWithPause(1, '\033[95m', f'You got {key}.')

            if i == 1:
                choices = ['regen', 'shield', 'baton', 'knife', 'gun']

                for item in [item for item in ['shield', 'baton'] if item in pro.inventory]:
                    choices.remove(item)

                getChoicesOfItemsFromList(pro, choices)

            elif i == 2:
                choices = ['gas canister', 'radio', 'drone', 'hissing cockroach', 'vial of diseased blood', 'armor',
                           'sword']

                for item in [item for item in ['gas canister', 'radio', 'drone', 'hissing cockroach',
                                               'vial of diseased blood'] if item in pro.inventory]:
                    choices.remove(item)

                getChoicesOfItemsFromList(pro, choices)

            elif i == 3:
                choices = ['gas canister', 'radio', 'hissing cockroach', 'armor']

                for item in [item for item in ['gas canister', 'radio', 'hissing cockroach'] if item in pro.inventory]:
                    choices.remove(item)

                if len(choices) > 1:
                    getChoicesOfItemsFromList(pro, choices)

                else:
                    pro.inventory.append('armor')
                    printWithPause(1, '\033[95m', 'You got armor.')

        if initialLevel == 2:
            pro.potions = 5

        else:
            pro.potions = 25


startGame()
loadGame()

action = None

while action != 'y':
    action = getInput('\033[96m', "Type 'y' to play or 'b' to view your bestiary:")

    if action == 'b':
        pro.showBestiary()

while True:
    while pro.hp > 0:
        saveGame()
        removeFoes()
        printWithPause(0.5, '\033[96m', f'{level}-{room}')
        returnedVar = pro.performNecessaryFunctions(foes, level)
        foes += pro.newFoes
        pro.newFoes = []

        if returnedVar == 1:
            if level == 4:
                handleLevelFourBossSpawn()

            elif room < 6:
                addFoes()
                showRegularRoomSwitchingText()

                if level == 3:
                    canonCooldown = room + 4
                    printWithPause(0.5, '\033[96m', f'The canon must readjust its aim. You will be '
                                                    f'shot by a canon in {canonCooldown} turns.')

            elif room == 6:
                addBoss()

            else:
                level += 1
                room = 0
                addFoes()
                play(songsPerLevel[level])

            removeFoes()

        elif returnedVar == 'terminal':
            getCustomInput()

        else:
            removeFoes()
            possessedFoes = [adversary for adversary in foes if adversary.possessed]
            targetList = [[pro]]

            if possessedFoes:
                targetList.append(possessedFoes)

            if 'drone' in pro.inventory:
                targetList.append([pro.drone])

            for enemy in foes:
                if not enemy.possessed:
                    enemy.actAsFoe(random.choice(random.choice(targetList)), number, foes, pro)

                else:
                    try:
                        otherFoes = [enemy for enemy in foes if not enemy.possessed]
                        enemy.actAsFoe(random.choice(otherFoes), number, foes, pro)

                    except IndexError:
                        pass

                addSummons(enemy)

            handleCanon()
            removeFoes()
            handleLevelFourSpawning()

    if level == 1:
        play('betterOp28No20Chopin.mp3')
        printWithPause(5, '\033[91m', 'You died. The alien troops will destroy the world.')

    elif level < 4:
        play('betterOp28No20Chopin.mp3')
        printWithPause(5, '\033[91m', 'You died. The alien troops will return. Without you, they will '
                       'have little resistance in destroying the world.')

    elif not victorious:
        play('betterOp28No20Chopin.mp3')
        printWithPause(5, '\033[91m', "Your efforts were all for nothing. The alien troops will return "
                       "to destroy the world.")

    else:
        printWithPause(5, '\033[96m', 'You won.')

    saveGame()

    if getInput('\033[96m', f'Will you play again? y/n:') == 'y':
        for i in range(200):
            print('')

        handleDeath()
        play(songsPerLevel[level])

    else:
        saveGame()
        sys.exit()
