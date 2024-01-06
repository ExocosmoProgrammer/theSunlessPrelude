import random

from variables import foesPerLevel, bossesPerLevel, oneTimeUseItems
from definitions import printWithPause, percentChance, greater, saveWithPickle
from player import player
from foe import foe

number = 2
room = 1
level = 1
pro = player()
foes = [foe('alien soldier', 1)]
printWithPause('Day 12', 3)
levelFourSpawnCooldown = 0
playerClass = None
canonCooldown = 3

file = 0

while file not in [1, 2, 3, 4]:
    try:
        file = int(input('Choose your file. Type the file number in 1-4:'))

    except ValueError:
        pass

while playerClass not in ['police', 'soldier', 'citizen']:
    playerClass = input("Pick your class. The choices are 'police', 'soldier', and 'citizen':")

if playerClass == 'police':
    pro.maxHp = 75
    pro.inventory = ['gun', 'baton']

elif playerClass == 'soldier':
    pro.maxHp = 100
    pro.inventory = ['knife', 'shield', 'cross', 'nunchucks', 'sacrificial dagger', 'radio', 'hissing cockroach',
                     'gas canister', 'vial of diseased blood', 'stun grenade', 'baton', 'gun', 'regen',
                     'butterfly knife']
    pro.inventory = ['knife', 'shield']
    pro.updateStats()

elif playerClass == 'citizen':
    pro.maxHp = 150
    pro.inventory = ['regen'] * 2

pro.hp = pro.maxHp
pro.initialHp = pro.hp


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
        printWithPause("You found an alien commander.", 2)
        printWithPause('Kill the commander.', 2)

    elif level == 2:
        printWithPause("You reached the ship's cockpit.", 2)
        printWithPause("If you manage to kill the pilot, you will gain "
                       "control of the ship.", 2)
        printWithPause('Kill the pilot.', 2)

    elif level == 3:
        printWithPause("You reached the room where you can regain access "
                       "to the ship's controls.", 2)
        printWithPause("The room is being guarded by an alien warrior.", 2)
        printWithPause("Kill the warrior.", 2)

    room = 5


def removeFoes():
    global foes, number

    for enemy in foes:
        if enemy.hp <= 0:
            foes.remove(enemy)
            getRidOfFoe = 1

            if 'cross' in pro.inventory and not enemy.possessed and enemy.type not in ['alien commander',
                                                                                       'alien pilot', 'alien warrior',
                                                                                       'sun priest']:
                if len(pro.souls) < 2:
                    if input(f"Will you take {enemy.getPrintName()}'s soul? y/n:") == 'y':
                        enemy.hp = enemy.initialHp / 2
                        enemy.attack /= 2
                        enemy.possessed = 1
                        enemy.controlledByPro = 1
                        pro.souls.append(enemy)
                        enemy.scanned = 1
                        printWithPause(f"You gained {enemy.getPrintName()}'s soul, costing you {enemy.hp} hp.")
                        pro.hp -= enemy.hp
                        enemy.bleedingDamage = 0
                        enemy.poisonDamage = 0
                        enemy.stun = 0
                        getRidOfFoe = 0

                    else:
                        printWithPause(f'{enemy.getPrintName()} is dead.')
                        printWithPause(f"You left behind {enemy.getPrintName()}'s soul.")

                else:
                    printWithPause("You cannot hold another soul.")

            if getRidOfFoe:
                printWithPause(f'{enemy.getPrintName()} is dead.')

                if level == 4:
                    pro.enemiesKilledInLevelFour += 1

                for key in enemy.loot.keys():
                    if percentChance(enemy.loot[key]) and (key not in oneTimeUseItems or
                                                           pro.inventory.count(key) < 3):
                        pro.inventory.append(key)
                        printWithPause(f'You got {key}.', 1)

                if enemy.givesPotions and percentChance(25):
                    pro.potions += 1
                    printWithPause('You acquired a potion.')

            if enemy.type == 'alien commander':
                foes = []
                pro.potions += 5
                number = 1
                printWithPause(f'You got 5 potions.')
                printWithPause('You killed the alien commander. ', 4)
                printWithPause('The alien leaders, '
                               'realizing the futility of attacking the world while you live, '
                               'remove their troops.', 4)
                printWithPause('However, your victory was temporary. Once you '
                               'die, the troops will finish destroying the world.', 4)
                printWithPause('You can do more to help stop the '
                               'aliens.', 4)
                printWithPause("Disguised as an alien soldier, you board a "
                               "retreating ship.", 4)
                printWithPause('Continued in chapter II...', 5)
                pro.hasReachedLevelTwo = 1
                break

            elif enemy.type == 'alien pilot':
                foes = []
                pro.potions += 5
                number = 1
                printWithPause('You got 5 potions.')
                printWithPause("Before you can finish killing the pilot, he disables "
                               "the ship's controls and alerts other pilots that "
                               "the ship is being taken over.", 6)
                printWithPause('The pilot is dead now.', 4)
                printWithPause("The ship's controls must be re-enabled from "
                               "another room.", 4)
                printWithPause('Make your way to the room to gain control of your '
                               'ship.', 5)
                printWithPause("The pilots that know that your ship is being hijacked "
                               "prepare to shoot your ship with their canons.", 5)
                printWithPause('Continued in chapter III...', 5)

            elif enemy.type == 'alien warrior':
                pro.potions += 25
                number = 1
                printWithPause('You got 25 potions.')
                printWithPause("You killed the alien warrior.", 4)
                printWithPause("You re-enable the ship's controls and make your way back "
                               "to the cockpit.", 5)
                printWithPause('...', 5)
                printWithPause("Your ship is significantly quicker than the others. "
                               "You are able to escape.", 7)
                printWithPause("...", 5)
                printWithPause("You find the aliens' planet.", 5)
                printWithPause("...", 5)
                printWithPause("You have arrived.", 5)
                printWithPause("Cause chaos.", 5)
                printWithPause('Continued in chapter IV...', 5)
                pro.hasReachedLevelFour = 1

            elif enemy.type == 'sun priest':
                while input('Will you proceed? y/n:') != 'y':
                    pass

                printWithPause('You killed the sun priest.', 5)
                printWithPause("You are victorious.", 5)
                printWithPause("You sit back and wait to die, glad to have saved your planet.", 5)
                printWithPause("Once you killed the priest, Earth's sun "
                               "disappeared.", 5)
                printWithPause("...", 5)
                printWithPause("Without the sun, Earth goes cold and dark.", 5)
                printWithPause("All life on Earth's surface is gone.", 5)
                printWithPause("The alien troops will never attack your "
                               "planet again.", 5)
                printWithPause('You died.', 10)

                while True:
                    pass


def handleCanon():
    global canonCooldown

    if level == 3 and room < 5:
        canonCooldown -= 1

        if canonCooldown <= 0:
            canonCooldown = room + 3
            pro.hp -= 40
            printWithPause(f'You were hit by a canon shot, inflicting 40 damage.')

            for enemy in foes:
                enemy.hp -= 40
                printWithPause(f'{enemy.getPrintName()} was shot by a canon, inflicting 40 damage')

            removeFoes()

        else:
            printWithPause(f'There are {canonCooldown} turns until you are shot by a canon.')


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
                printWithPause(f'{foes[-1].getPrintName()} appeared.')
                number += 1
                levelFourSpawnCooldown = 6

        levelFourSpawnCooldown -= 1


def handleLevelFourBossSpawn():
    global foes, number
    pro.sunPriestSpawned = 1
    foes = [foe('sun priest', number, scanned=1)]
    printWithPause("You escaped the mob attacking you and fled to the cathedral.", 5)
    printWithPause("Inside the cathedral, you found the priest controlling Earth's sun.", 5)
    printWithPause('Kill the priest.', 5)
    number += 1


def saveGame():
    saveWithPickle(pro, f'playerSave{file}.py')
    variousData = {}


while pro.hp > 0:
    removeFoes()
    printWithPause(f'{level}-{room}')
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
            printWithPause(f'The canon must readjust its aim. You will be shot by a '
                           f'canon in {canonCooldown} turns.')

        removeFoes()

    else:
        removeFoes()
        addSummons()
        possessedFoes = [adversary for adversary in foes if adversary.possessed]

        for enemy in foes:
            if not enemy.possessed:

                if possessedFoes and percentChance(50):
                    enemy.actAsFoe(random.choice(possessedFoes), number, foes, pro)

                else:
                    enemy.actAsFoe(pro, number, foes, pro)
                    addSummons()

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
    printWithPause('You died. The alien troops will destroy the world.', 5)

elif level < 4:
    printWithPause('You died. The alien troops will return. Without you, they will '
                   'have little resistance in destroying the world.', 5)

else:
    printWithPause("Your efforts were all for nothing. The alien troops will return "
                   "to destroy the world.", 5)

printWithPause('Game over', 2)

while True:
    pass
