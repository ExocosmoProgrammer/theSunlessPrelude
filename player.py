import random
import copy
import sys
import os
import time

from definitions import (lesser, printWithPause, getReducedDamage, percentChance, getTarget,
                         getListOfThingsWithCommas, greater, getInput, getRandomItemsFromList, ceiling,
                         printInRainbowWithPause, strIndex, play)
from variables import (oneTimeUseItems, hpPerFoe, attackPerFoe, lootPerFoe, descriptionPerFoe, combatInfoPerFoe,
                       bestiaryOrder)
from drone import drone
from movementPuzzleFoe import movementPuzzleFoe


class player:
    def __init__(self, **extra):
        self.maxHp = 100
        self.hp = 100
        self.initialHp = 100
        self.inventory = []
        self.foe = 0
        self.attack = 10
        self.potions = 3
        self.blocking = 0
        self.damageReduction = 0
        self.stun = 0
        self.souls = []
        self.newFoes = []
        self.enemiesKilledInLevelFour = 0
        self.durationInLevelFour = 0
        self.sunPriestSpawned = 0
        self.sunPriestSpotted = 0
        self.standardAttack = 10
        self.temporaryAttack = 0
        self.temporaryAttackDuration = 0
        self.hasReachedLevelFour = 0
        self.hasReachedLevelTwo = 0
        self.drone = drone()
        self.strongDroneForCommander = drone(empowered=True)
        self.isDrone = 0
        self.poisonDamage = 0
        self.turnsOfPoisonDamage = 0
        self.bleedingDamage = 0
        self.turnsOfBleedingDamage = 0
        self.burningDamage = 0
        self.turnsOfBurningDamage = 0
        self.foesEncountered = []
        self.lockedBoxPuzzles = [self.playTicTacToe, self.playWhereIsWaldo,
                                 self.playMovementPuzzle]
        self.playerSpace = [0, 0]
        self.board = {}
        self.experimentalBoard = {}
        self.warriorFound = False
        self.highestFootprintNumberFound = 0
        self.rageCooldown = 7
        self.rageDuration = 0
        self.adrenalineCooldown = 7
        self.adrenalineDuration = 0
        self.damageMultiplierForAttackType = 1
        self.song = "The War.mp3"
        self.availableClasses = ['police', 'soldier', 'citizen']
        self.lastSongPlayed = None

        for key in extra.keys():
            exec(f'self.{key} = extra[key]')

    def showHp(self):
        """Displays the player's hp and inventory."""
        hpDashCount = int(self.hp / 10)
        emptySpaceCount = int(self.maxHp / 10 - hpDashCount)
        upgradeInventory = [item for item in self.inventory if item not in oneTimeUseItems]
        oneTimeItemInventory = [item for item in self.inventory if item in oneTimeUseItems]
        printWithPause(0.5, '\033[96m', f'You have {self.hp} hit points and {self.potions} potions.')
        printWithPause(0.5, '\033[97m', '[', '\033[91m', f'{"_" * hpDashCount}{" " * emptySpaceCount}',
                       '\033[97m', ']')
        printWithPause(0.5, '\033[96m', "Upgrade items: ", '\033[97m', f"{upgradeInventory}")

        if oneTimeItemInventory:
            printWithPause(0.5, '\033[96m', "One time use items: ", '\033[97m', f"{oneTimeItemInventory}")

        if self.souls:
            printWithPause(0.5, '\033[96m', "Souls: ", '\033[97m', f"{[enemy.fullName for enemy
                                                                       in self.souls]}")

    def heal(self, amount):
        """self.heal(x) heals self by x hit points and then reduces self.hp to self.maxHp if
        self.hp exceeds the self.maxHp."""
        self.hp = lesser(self.hp + amount, self.maxHp)

    def getRegen(self):
        """Regenerates the player's hp from the 'regen' item each turn as needed."""

        for i in range(self.inventory.count('regen')):
            oldHp = self.hp
            self.heal(3)
            printWithPause(0.5, '\033[96m', f'You regained {self.hp - oldHp} hit points.')

    def activateRage(self):
        self.rageCooldown = 7
        self.rageDuration = 2
        self.updateStats()

    def activateAdrenaline(self):
        self.adrenalineCooldown = 7
        self.adrenalineDuration = 2

    def basicAttack(self, enemies):
        """self.basicAttack(self, enemies) makes self perform  basic attack."""

        if self.rageCooldown <= 0 and getInput('\033[96mWould you like to activate rage? Type y/n:') == 'y':
            self.activateRage()

        if 'sacrificial dagger' in self.inventory and self.attack == self.standardAttack and not \
                [enemy for enemy in enemies if enemy.type == 'helpless sun priest'] \
                and getInput('\033[96m', "Will you use your sacrificial dagger? y/n:") == 'y':
            self.useSacrificialDagger()
            self.updateStats()

        attackType = None
        damageMultipliers = {'l': 0.4, 'r': 1, 'h': 3}

        while attackType not in ['l', 'r', 'h']:
            attackType = getInput("\033[96mPress 'l' to perform two light attacks, 'r' to perform a regular attack, or "
                                  "'h' to perform a heavy attack:")

        self.damageMultiplierForAttackType = damageMultipliers[attackType]

        if enemies:
            for i in range(2 if attackType == 'l' else 1):
                targetId = getInput('\033[96m', "Enter the id number of the foe that you want to attack or "
                                                "'r' to attack a random foe:")

                enemy = getTarget(enemies, targetId)
                # If your input on who to attack is invalid, then targetId will be equal to none and
                # the code in the next try block will raise Attribute Error.

                try:
                    if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                         foe.type in ['alien worshipper',
                                                                                                      'alien cardinal']
                                                                                         and foe.hp > 0 and foe.possessed ==
                                                                                         enemy.possessed]:
                        attackedFoe = random.choice([foe for foe in enemies if
                                                     foe.type in ['alien worshipper', 'alien cardinal']
                                                     and foe.hp > 0 and foe.possessed ==
                                                     enemy.possessed])
                        attackedFoe.hp = 0
                        printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of '
                                                        f'your attack.')

                    elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                              foe.type == 'alien protector']:
                        printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()}, but they were '
                                                        f'immune.')

                    else:
                        if percentChance(50):
                            damageInflicted = getReducedDamage(self.attack, enemy) * self.damageMultiplierForAttackType
                            printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()}, inflicting '
                                                            f'{damageInflicted} '
                                                            f'damage.')

                        else:
                            damageInflicted = getReducedDamage(self.attack, enemy) * 2 * \
                                              self.damageMultiplierForAttackType
                            printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with a '
                                                            f'critical attack, inflicting {damageInflicted} damage.')

                        enemy.hp -= damageInflicted
                        # enemy.twirlingNunchucks is 1 if the enemy is a nun or mother superior that is
                        # using its ability of twirling nunchucks else 0.

                        if enemy.twirlingNunchucks:
                            self.hp -= self.attack
                            printWithPause(0.5, '\033[91m', f'{enemy.getPrintName()} deflected your attack '
                                                            f'with their nunchucks, inflicting {damageInflicted} '
                                                            f'damage to you.')

                        if 'baton' in self.inventory:
                            enemy.beHitByBaton(self)

                        if enemy.gunWeakness and 'gun' in self.inventory:
                            if enemy.type == 'alien commander' and [protector for protector in
                                                                    enemies if protector.type
                                                                               == 'alien protector']:
                                printWithPause(0.5, '\033[93m', f'You shot {enemy.getPrintName()}, but '
                                                                f'they were immune.')

                            else:
                                damageInflicted = getReducedDamage(self.attack * 3 / 4 * \
                                                                   self.damageMultiplierForAttackType, enemy)

                                if enemy.twirlingNunchucks:
                                    for i in range(self.inventory.count('gun')):
                                        printWithPause(0.5, '\033[91m', f'You shot at {enemy.getPrintName()}, '
                                                                        f'but they deflected your bullet back at you, '
                                                                        f'inflicting {damageInflicted} damage to you.')
                                        self.hp -= self.attack * 3 / 4

                                else:
                                    for i in range(self.inventory.count('gun')):
                                        printWithPause(0.5, '\033[93m', f'You shot {enemy.getPrintName()}, '
                                                                        f'inflicting {damageInflicted} damage.')
                                        enemy.hp -= damageInflicted

                                enemy.bleedingDamageFromGun = 6
                                enemy.turnsOfBleedingFromGun = 3

                    self.rageCooldown -= 1

                except AttributeError:
                    pass

        else:
            printWithPause(0.5, '\033[96m', 'You are in an empty room.')

        if attackType == 'h':
            self.stun = 1
            printWithPause(0.5, '\033[96mYou were stunned by your heavy attack.')

    def scan(self, enemies):
        """self.scan(enemies) makes the player scan."""
        print('')
        printWithPause(0.5, '\033[96m', 'The enemies in your room are:')

        if 'radio' in self.inventory:
            for enemy in enemies:
                enemy.scanned = 1
                printWithPause(0.5, '\033[96m', f'   {enemy.fullName} with {enemy.hp} hp')

        else:
            for enemy in enemies:
                printWithPause(0.5, '\033[96m', f'   {enemy.getPrintName()} with {enemy.hp} hp')
                enemy.scanned = 1

        print('')

    def knifeAttack(self, enemies):
        """Makes the player perform two attacks with their knife."""
        targetId = getInput('\033[96m', "Enter the id number of the foe that you want to stab with "
                                        "your knife or 'r' to stab a random foe:")
        enemy = getTarget(enemies, targetId)
        # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
        # loop will raise Attribute Error.

        try:
            if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                 foe.type in ['alien worshipper',
                                                                                              'alien cardinal']
                                                                                 and foe.hp > 0 and foe.possessed ==
                                                                                 enemy.possessed]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type in ['alien worshipper', 'alien cardinal']
                                             and foe.hp > 0 and foe.possessed ==
                                             enemy.possessed])
                attackedFoe.hp = 0
                printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of your '
                                                f'attack.')

            elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                      foe.type == 'alien protector']:
                printWithPause(0.5, '\033[93m', f'You stabbed {enemy.getPrintName()}, but they were '
                                                f'immune.')

            else:
                damageInflicted = getReducedDamage(self.attack / 2, enemy)
                printWithPause(0.5, '\033[93m', f'You stabbed {enemy.getPrintName()} '
                                                f'with your knife, inflicting '
                                                f'{damageInflicted} damage.')
                enemy.hp -= damageInflicted

                if enemy.twirlingNunchucks:
                    self.hp -= self.attack / 2
                    printWithPause(0.5, '\033[91m', f'{enemy.getPrintName()} deflected your stab '
                                                    f'with their nunchucks, inflicting {damageInflicted} damage '
                                                    f'to you.')

        except AttributeError:
            pass

    def butterflyKnifeAttack(self, enemies):
        """Makes the player perform two attacks with their butterfly knife."""

        for i in range(2):
            targetId = getInput('\033[96m', "Enter the id number of a foe that you want to slash with "
                                            "your butterfly knife or 'r' to slash a random foe:")
            enemy = getTarget(enemies, targetId)
            # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
            # loop will raise Attribute Error.

            try:
                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                     foe.type in ['alien worshipper',
                                                                                                  'alien cardinal']
                                                                                     and foe.hp > 0 and foe.possessed ==
                                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type in ['alien worshipper', 'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of '
                                                    f'your attack.')

                elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                          foe.type == 'alien protector']:
                    printWithPause(0.5, '\033[93m', f'You slashed {enemy.getPrintName()}, but they '
                                                    f'were immune.')

                else:
                    damageInflicted = getReducedDamage(self.attack * 3 / 8, enemy)
                    printWithPause(0.5, '\033[93m', f'You slashed {enemy.getPrintName()} '
                                                    f'with your butterfly knife, inflicting '
                                                    f'{damageInflicted} damage.')
                    enemy.hp -= damageInflicted

                    if enemy.twirlingNunchucks:
                        self.hp -= self.attack * 3 / 8
                        printWithPause(0.5, '\033[91m', f'{enemy.getPrintName()} deflected your slash '
                                                        f'with their nunchucks, inflicting {damageInflicted} damage '
                                                        f'to you.')

            except AttributeError:
                pass

    def useNunchucks(self, enemies):
        """Makes the player attack with their nunchucks."""
        targetId = getInput('\033[96m', "Enter the id number of the foe that you want to hit with your nunchucks "
                                        "or 'r' to hit a random foe.")
        enemy = getTarget(enemies, targetId)
        # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
        # loop will raise Attribute Error.

        try:
            if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                 foe.type in ['alien worshipper',
                                                                                              'alien cardinal']
                                                                                 and foe.hp > 0 and foe.possessed ==
                                                                                 enemy.possessed]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type in ['alien worshipper', 'alien cardinal']
                                             and foe.hp > 0 and foe.possessed ==
                                             enemy.possessed])
                attackedFoe.hp = 0
                printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of '
                                                f'your attack.')

            elif enemy.type == 'alien commander' and [foe for foe in enemies if enemy.type == 'alien protector']:
                printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()}, but they were immune.')

            else:
                damageInflicted = getReducedDamage(10, enemy)
                printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} '
                                                f'with your nunchucks, inflicting {damageInflicted} damage.')
                enemy.hp -= damageInflicted
                enemy.nunchuckDebuff = 1

                if enemy.twirlingNunchucks:
                    self.hp -= 10
                    printWithPause(0.5, '\033[91m', f'{enemy.getPrintName()} deflected your attack '
                                                    f'with their nunchucks, inflicting 10 damage '
                                                    f'to you.')

        except AttributeError:
            pass

    def useSolution(self, enemies):
        """Makes the player use a solution."""

        if 'solution' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe that you want to throw your solution at '
                                            "or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)
            # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
            # loop will raise Attribute Error.

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    self.inventory.remove('solution')
                    otherFoes = enemies[:]
                    otherFoes.remove(enemy)

                    if otherFoes:
                        theNun = enemy
                        enemy = random.choice(otherFoes)
                        printWithPause(0.5, '\033[96m', f'{theNun.getPrintName()} used their nunchucks to '
                                                        f'deflect your solution towards {enemy.getPrintName()}.')

                    else:
                        printWithPause(0.5, '\033[96m', f'{enemy.getPrintName} reflected your solution '
                                                        f'with their nunchucks.')
                        raise AttributeError

                if enemy.type in ['alien pilot', 'alien warrior', 'sun priest']:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} is immune to your solution.')

                elif enemy.type in ['alien priest', 'alien bishop'] and \
                        [foe for foe in enemies if foe.type in ['alien worshipper',
                                                                'alien cardinal'] \
                                                   and foe.hp > 0 and foe.possessed ==
                                                   enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if foe.type in ['alien worshipper',
                                                                                        'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.possessed = 1
                    printWithPause(0.5, '\033[96m', f'{attackedFoe.getPrintName()} got in the way of '
                                                    f'your solution.')

                else:
                    printWithPause(0.5, '\033[96m', f'You hit {enemy.getPrintName()} with your solution, '
                                                    f'causing them to be possessed by you.')
                    enemy.possessed = 1
                    self.inventory.remove('solution')

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a solution.')

    def useThrowingKnife(self, enemies):
        """Makes the player use a throwing knife."""
        # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
        # loop will raise Attribute Error.

        if 'throwing knife' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe that you want to throw your knife '
                                            "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your throwing knife back at you.')
                    printWithPause(0.5, '\033[91m', 'You got poisoned.')
                    self.poisonDamage = greater(self.poisonDamage, 5)
                    self.turnsOfPoisonDamage = 10
                    self.inventory.remove('throwing knife')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                     foe.type in ['alien worshipper',
                                                                                                  'alien cardinal']
                                                                                     and foe.hp > 0 and foe.possessed ==
                                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type in ['alien worshipper', 'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way '
                                                    f'of your knife.')

                else:
                    printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with your '
                                                    f'knife, poisoning them.')
                    enemy.poisonDamage = greater(5, enemy.poisonDamage)

                self.inventory.remove('throwing knife')

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a throwing knife.')

    def useStunGrenade(self, enemies):
        """Makes the player use a stun grenade."""

        if 'stun grenade' in self.inventory:
            for enemy in [enemy for enemy in enemies if not enemy.possessed]:
                enemy.stun = 2
                printWithPause(0.5, '\033[96m', f'You stunned {enemy.getPrintName()} with your '
                                                f'stun grenade.')

            self.inventory.remove('stun grenade')

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a stun grenade.')

    def useVialOfPoison(self, enemies):
        """Makes the player use a vial of poison."""

        if 'vial of poison' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe that you want to throw your vial '
                                            "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)
            # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
            # loop will raise Attribute Error.

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} hit your vial of poison '
                                                    f'with their nunchucks. Your vial of poison shattered, covering '
                                                    f'the nun with poison. The nun is now poisoned')
                    enemy.poisonDamage = 15

                elif enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                       foe.type in ['alien worshipper',
                                                                                                    'alien cardinal']
                                                                                       and foe.hp > 0 and foe.possessed ==
                                                                                       enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type in ['alien worshipper', 'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[96m', f'{attackedFoe.getPrintName()} got in the way of '
                                                    f'your attack.')

                else:
                    printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with your vial, '
                                                    f'poisoning them.')
                    enemy.poisonDamage = 15

                self.inventory.remove('vial of poison')

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a vial of poison.')

    def useSerratedKnife(self, enemies):
        """Makes the player use a serrated knife."""
        # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
        # loop will raise Attribute Error.

        if 'serrated knife' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe that you want to throw your '
                                            "serrated knife at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your serrated knife back at you.')
                    printWithPause(0.5, '\033[91m', 'You are now bleeding.')
                    self.bleedingDamage = greater(self.bleedingDamage, 5)
                    self.turnsOfBleedingDamage = 10
                    self.inventory.remove('serrated knife')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                     foe.type in ['alien worshipper',
                                                                                                  'alien cardinal']
                                                                                     and foe.hp > 0 and foe.possessed ==
                                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type in ['alien worshipper', 'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of '
                                                    f'your attack.')

                else:
                    printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with your knife, '
                                                    f'causing them to bleed.')
                    enemy.bleedingDamage = 5

                self.inventory.remove('serrated knife')

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a serrated knife.')

    def useCombustibleLemon(self, enemies):
        """Makes the player use a combustible lemon."""

        if 'combustible lemon' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe that you want to throw your combustible '
                                            "lemon at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)
            # If your input on who to attack is invalid, then targetId will be equal to none and the code in the try
            # loop will raise Attribute Error.

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your combustible lemon back at you.')
                    printWithPause(0.5, '\033[91m', 'You are now burning and poisoned.')
                    self.burningDamage = greater(self.burningDamage, 5)
                    self.turnsOfBurningDamage = 10
                    self.poisonDamage = greater(self.poisonDamage, 5)
                    self.turnsOfPoisonDamage = 10
                    self.inventory.remove('combustible lemon')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                                     foe.type in ['alien worshipper',
                                                                                                  'alien cardinal']
                                                                                     and foe.hp > 0 and foe.possessed ==
                                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type in ['alien worshipper', 'alien cardinal']
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way '
                                                    f'of your attack.')

                else:
                    printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with your '
                                                    f'combustible lemon, poisoning them. The lemon combusted, '
                                                    f'burning {enemy.getPrintName()}.', 2)
                    enemy.poisonDamage = 15
                    enemy.burnDamage = 15

                self.inventory.remove('combustible lemon')

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a combustible lemon.')

    def useOneTimeUseItem(self, enemies):
        """Gets the player's input on what one time use item to use and tries to use the requested type of one
        time use item."""
        print('')
        printWithPause(0.5, '\033[96m', 'Your one time use items are:')

        for item in self.inventory:
            if item in oneTimeUseItems:
                printWithPause(0.5, '\033[97m', f'   {item}')

        print('')
        itemUsed = getInput('\033[96m', f'What item will you use:')

        if itemUsed == 'solution':
            self.useSolution(enemies)

        elif itemUsed == 'throwing knife':
            self.useThrowingKnife(enemies)

        elif itemUsed == 'stun grenade':
            self.useStunGrenade(enemies)

        elif itemUsed == 'vial of poison':
            self.useVialOfPoison(enemies)

        elif itemUsed == 'serrated knife':
            self.useSerratedKnife(enemies)

        elif itemUsed == 'combustible lemon':
            self.useCombustibleLemon(enemies)

    def usePotion(self):
        """Makes the player use a potion."""

        if self.potions > 0:
            oldHp = self.hp
            self.heal(50)
            printWithPause(0.5, '\033[96m', f'You used a potion. You regained {self.hp - oldHp} '
                                            f'hit points.')
            self.potions -= 1

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a potion.')

    def updateStats(self):
        """Properly adjusts the player's attack, temporary attack duration, and maximum hp."""
        self.standardAttack = 10 + self.inventory.count('sword') * 5
        self.maxHp = self.initialHp + self.inventory.count('armor') * 15
        self.attack = self.temporaryAttack + self.standardAttack
        self.temporaryAttackDuration -= 1

        if self.blocking:
            self.damageReduction = 75

        else:
            self.damageReduction = 0

        if self.temporaryAttackDuration <= 0:
            self.temporaryAttack = 0

        if self.rageDuration > 0:
            self.attack *= 1.5

        if self.adrenalineDuration > 0:
            self.damageReduction = lesser(self.damageReduction + 50, 100)

        self.rageDuration -= 1
        self.adrenalineDuration -= 1

    def releaseSoul(self):
        """Gets player input on what soul to release and tries to release the soul that the player says to release."""

        try:
            soulId = getInput('\033[96m', "Type the id of the soul that you want to release:")
            soul = [enemy for enemy in self.souls if enemy.number == int(soulId)][0]
            self.souls.remove(soul)
            self.newFoes.append(soul)
            printWithPause(0.5, '\033[96m', f"You released the soul of {soul.getPrintName()}.")

        except (ValueError, IndexError):
            pass

    def useSacrificialDagger(self):
        """Makes the player use their sacrificial dagger."""

        try:
            hpSacrificed = int(getInput('\033[96m', 'How much hp will you turn into extra temporary attack:'))

            if hpSacrificed > 0:
                printWithPause(0.5, '\033[91m', f'You got {hpSacrificed} extra temporary attack and '
                                                f'lost {hpSacrificed} hp.')
                self.temporaryAttackDuration = 2
                self.temporaryAttack = hpSacrificed
                self.hp -= hpSacrificed

        except ValueError:
            pass

    def getCustomInput(self):
        """Gets player input until 'y' is entered in. Tries to execute each response from the getCustomInput method."""
        action = getInput('\033[96m', "What will you do? Type 'y' to exit the terminal for custom inputs:")
        # self.getCustomInput() is only called in the self.actions method. If self.getCustomInput returns 1, then
        # self.actions will return 1, causing the getCustomInput function to be called in the game file.

        if action == 'other':
            return 1

        elif action != 'y':
            try:
                exec(action)

            except Exception as error:
                printWithPause(0.5, '\033[91m', f'Your command raised an error saying, "{error}."')

            self.getCustomInput()

        return 0

    def actions(self, enemies, level):
        """Handles all of the player's actions."""
        self.blocking = 0
        self.damageReduction = 0
        self.updateStats()

        if not self.sunPriestSpotted and self.enemiesKilledInLevelFour >= 15:
            self.sunPriestSpotted = 1
            printWithPause(5, '\033[95m', "You have made a gap in the mob surrounding you. "
                                          "Through the gap, you see a cathedral in the distance.")

        if self.stun:
            self.stun = 0
            printWithPause(0.5, '\033[96m', 'You are stunned.')

        else:
            if self.adrenalineCooldown <= 0 and getInput('\033[96mWould you like to activate adrenaline? Enter y/n:') \
                    == 'y':
                self.activateAdrenaline()

            actionList = ["Type 'a' to perform a basic attack", "'s' to scan"]

            if self.potions:
                actionList.append("'h' to use a potion")

            if [item for item in self.inventory if item in oneTimeUseItems]:
                actionList.append("'c' to use a one time use item")

            if 'shield' in self.inventory:
                actionList.append("'b' to block")

            if 'nunchucks' in self.inventory:
                actionList.append("'n' to use your nunchucks")

            if self.souls:
                actionList.append("'r' to release a soul")

            if self.lockedBoxPuzzles:
                actionList.append("'p' to progress in opening your locked box")

            if not [enemy for enemy in enemies if not enemy.possessed] and level < 4 or (self.enemiesKilledInLevelFour
                                                                                         >= 15
                                                                                         and not self.sunPriestSpawned):
                actionList.append("'y' to progress to the next area")

            action = getInput('\033[96m', getListOfThingsWithCommas('or', actionList, ':'))

            if not [enemy for enemy in enemies if enemy.type == 'helpless sun priest']:
                if action == 'a':
                    self.basicAttack(enemies)

                elif action == 's':
                    self.scan(enemies)

                elif action == 'h':
                    self.usePotion()

                elif action == 'b' and 'shield' in self.inventory:
                    self.blocking = 1
                    self.damageReduction = 75

                elif action == 'c' and [item for item in self.inventory if item in oneTimeUseItems]:
                    self.useOneTimeUseItem(enemies)

                elif action == 'n' and 'nunchucks' in self.inventory:
                    self.useNunchucks(enemies)

                elif action == 'r' and self.souls:
                    self.releaseSoul()

                elif action == 'p' and self.lockedBoxPuzzles:
                    self.tryToOpenBox()

                elif action == 'y' and (not [enemy for enemy in enemies if not enemy.possessed]
                                        and level < 4 or self.enemiesKilledInLevelFour >= 15):
                    return 1

                elif action == 'other' and self.getCustomInput():
                    return 'terminal'

                for i in range(self.inventory.count('knife')):
                    if [enemy for enemy in enemies if enemy.hp > 0 and not enemy.possessed]:
                        self.knifeAttack(enemies)

                for i in range(self.inventory.count('butterfly knife')):
                    if [enemy for enemy in enemies if enemy.hp > 0 and not enemy.possessed]:
                        self.butterflyKnifeAttack(enemies)

                if 'strong drone' in self.inventory:
                    self.strongDroneForCommander.actions(enemies, self)

                elif 'drone' in self.inventory:
                    self.drone.actions(enemies, self)

            else:
                enemies[0].hp -= 10

                if enemies[0].hp == 40:
                    printWithPause(1, '\033[93m', 'You hit the sun priest. You hear something crack.')

                elif enemies[0].hp == 30:
                    printWithPause(1, '\033[93m', 'You hit the sun priest. Blood stains your fists.')

                elif enemies[0].hp == 20:
                    printWithPause(1, '\033[93m', 'You hit the sun priest. Its face is disfigured '
                                                  'and broken.')

                elif enemies[0].hp == 10:
                    printWithPause(1, '\033[93m', 'You hit the sun priest. Something squelches.')

                elif enemies[0].hp == 0:
                    printWithPause(1, '\033[93m', 'You hit the sun priest. You hear nothing but '
                                                  'hollow blows and feel nothing but wet blood.')

    def getHurtByDebuffs(self):
        """Causes debuffs to hurt the player. Causes debuffs to stop hurting the player once the debuffs' durations
        are over."""

        if self.poisonDamage:
            self.hp -= self.poisonDamage
            printWithPause(0.5, '\033[91m', f'You took {self.poisonDamage} damage from poison.')

            if self.turnsOfPoisonDamage <= 0:
                self.poisonDamage = 0

            self.turnsOfPoisonDamage -= 1

        if self.bleedingDamage:
            self.hp -= self.bleedingDamage
            printWithPause(0.5, '\033[91m', f'You took {self.bleedingDamage} damage from bleeding.')

            if self.turnsOfBleedingDamage <= 0:
                self.bleedingDamage = 0

            self.turnsOfBleedingDamage -= 1

        if self.burningDamage:
            self.hp -= self.burningDamage
            printWithPause(0.5, '\033[91m', f'You took {self.burningDamage} damage from burning.')

            if self.turnsOfBurningDamage <= 0:
                self.burningDamage = 0

            self.turnsOfBurningDamage -= 1

    def performNecessaryFunctions(self, enemies, level):
        """Performs all of the player's methods as needed."""
        self.showHp()
        self.getRegen()
        self.getHurtByDebuffs()
        whatToReturn = self.actions(enemies, level)

        if not self.sunPriestSpawned:
            if level == 4:
                self.durationInLevelFour += 1

            if self.durationInLevelFour in [25, 37, 49, 61]:
                printWithPause(2, '\033[95m', "Aliens from further away than before are now aware of your "
                                              "presence and head off to attack you.")

        return whatToReturn

    def showBestiary(self):
        for enemy in [enemy for enemy in bestiaryOrder if enemy in self.foesEncountered or True]:
            print('')
            print(f'Name: {enemy}')
            print(f'Hp: {hpPerFoe[enemy]}')
            print(f'Attack: {attackPerFoe[enemy]}')

            try:
                print(f'Loot: {lootPerFoe[enemy]}')

            except KeyError:
                print('Loot: {}')

            print(f'Combat description: {combatInfoPerFoe[enemy]}')
            print(f'Other description: {descriptionPerFoe[enemy]}')

        print('')

    def getLinesInTicTacToe(self, board):
        lines = []

        for i in ['a', 'b', 'c']:
            lines.append({f'{i}1': self.board[f'{i}1'], f'{i}2': self.board[f'{i}2'], f'{i}3': self.board[f'{i}3']})

        for i in range(1, 4):
            lines.append({f'a{i}': self.board[f'a{i}'], f'b{i}': self.board[f'b{i}'], f'c{i}': self.board[f'c{i}']})

        lines.append({'a1': self.board['a1'], 'b2': self.board['b2'], 'c3': self.board['c3']})
        lines.append({'c1': self.board['c1'], 'b2': self.board['b2'], 'a3': self.board['a3']})
        return lines

    def showTicTacToeBoard(self, board):
        print('\033[97m', '      1     2     3')
        print('\033[97m', '   ------------------')

        for i in ['a', 'b', 'c']:
            print('\033[97m', f'{i} |  {self.board[f"{i}1"]}  |  {self.board[f"{i}2"]}  |  '
                              f'{self.board[f"{i}3"]}  |')
            print('\033[97m', '   ------------------')

    def showMovementPuzzle(self, board, visitedSpaces, requiredTiles):
        colorsForTiles = {'     ': '\033[00m', '  i  ': '\033[95m', ' ||| ': '\033[97m', '  !  ': '\033[91m',
                          '  o  ': '\033[93m'}
        print('\033[97m', '-------------------------------------------------------')

        for j in range(9):
            text = '|'

            for i in range(9):
                if self.board[(i, j)] == '     ':
                    hasFireball = False

                    for enemy in [enemy for enemy in self.board.values() if type(enemy) == movementPuzzleFoe]:
                        if [fireball for fireball in enemy.fireballs if fireball.coordinate == [i, j]]:
                            hasFireball = True
                            break

                    if hasFireball:
                        text += '\033[91m  *  \033[97m|'

                    elif [i, j] in requiredTiles and [i, j] not in visitedSpaces:
                        text += '\033[93m  o  \033[97m|'

                    else:
                        text += '     \033[97m|'

                elif type(self.board[(i, j)]) == movementPuzzleFoe:
                    text += self.board[(i, j)].__str__() + '\033[97m|'

                else:
                    text += colorsForTiles[self.board[(i, j)]] + self.board[(i, j)] + '\033[97m|'

            print('\033[97m', text)
            print('\033[97m', '-------------------------------------------------------')

    def playMovementPuzzle(self, mode):
        if mode == 'mysterious figure':
            printWithPause(2, "\033[91mThe mysterious figure removes their mask. "
                              "You see that they are actually...")
            play("newCommanderTheme.mp3", self, save=False)
            printWithPause(2, "The alien commander!")

        self.board = {}
        visitedSpaces = [[4, 8]]
        directionsPerKey = {'w': [0, -1], 'a': [-1, 0], 's': [0, 1], 'd': [1, 0]}
        requiredTiles = []

        for i in range(9):
            for j in range(9):
                self.board[(i, j)] = '     '

        for i in range(5):
            for j in range(5):
                self.board[(2 * j + 1, 2 * i + 1)] = ' ||| '

        if mode != 'mysterious figure' or True:
            for i in range(5):
                for j in getRandomItemsFromList([h * 2 for h in range(5)], 1):
                    self.board[(j, 2 * i + 1)] = ' ||| '

        self.playerSpace = [4, 8]
        self.board[(4, 8)] = '  i  '

        if mode == 'regular':
            xCoord = random.randint(0, 8)
            self.board[(xCoord, 0)] = movementPuzzleFoe([xCoord, 0],
                                                        random.choice(['mage', 'charging', 'basic']), self.board)

        elif mode == 'mysterious figure':
            self.board[(4, 0)] = movementPuzzleFoe([4, 0], 'mysterious figure', self.board)

        else:
            xCoord = random.randint(0, 8)
            self.board[(xCoord, 0)] = movementPuzzleFoe([xCoord, 0], mode, self.board)

            if mode == 'alien pilot':
                self.board[(xCoord, 6)] = movementPuzzleFoe([xCoord, 6],
                                                            random.choice(['mage', 'charging', 'basic']), self.board)

        if mode != 'mysterious figure':
            for i in [2, 4]:
                xCoord = random.randint(0, 8)
                self.board[(xCoord, i)] = movementPuzzleFoe([xCoord, i],
                                                            random.choice(['mage', 'charging', 'basic']), self.board)

        for i in range(9):
            requiredTiles.append(random.choice([list(key) for key in self.board.keys() if self.board[key] == '     ' and \
                                                key[1] == i]))

        def drawBoard():
            for i in range(200):
                print(' ')

            colorsForTiles = {'     ': '\033[00m', '  i  ': '\033[95m', ' ||| ': '\033[97m', '  !  ': '\033[91m',
                              '  o  ': '\033[93m'}
            print('\033[97m', '-------------------------------------------------------')

            for j in range(9):
                text = '|'

                for i in range(9):
                    if self.board[(i, j)] == '     ':
                        hasFireball = False

                        for enemy in [enemy for enemy in self.board.values() if type(enemy) == movementPuzzleFoe]:
                            fireballs = [fireball for fireball in enemy.fireballs if fireball.coordinate == [i, j]]

                            if fireballs:
                                hasFireball = True
                                harmfulFireballs = [fireball for fireball in fireballs if fireball.hurts]

                                if harmfulFireballs:
                                    sprite = harmfulFireballs[0].sprite

                                else:
                                    sprite = fireballs[0].sprite

                                break

                        if hasFireball:
                            text += f'\033[91m{sprite}\033[97m|'

                        elif [i, j] in requiredTiles and [i, j] not in visitedSpaces and mode != 'alien pilot':
                            text += '\033[93m  o  \033[97m|'

                        else:
                            text += '     \033[97m|'

                    elif type(self.board[(i, j)]) == movementPuzzleFoe:
                        text += self.board[(i, j)].__str__() + '\033[97m|'

                    else:
                        text += colorsForTiles[self.board[(i, j)]] + self.board[(i, j)] + '\033[97m|'

                print('\033[97m', text)
                print('\033[97m', '-------------------------------------------------------')

        def enemyTurns():
            for enemy in [value for value in self.board.values() if type(value) is movementPuzzleFoe]:
                if enemy.coordinate == self.playerSpace or '  i  ' in enemy.tilesSkipped or \
                        self.board[tuple(enemy.coordinate)] == '  i  ':
                    if enemy.type == 'alien warrior' and not [i for i in requiredTiles if i not in visitedSpaces]:
                        printWithPause(2, '\033[97m', 'You won.')
                        return 1

                    else:
                        printWithPause(2, '\033[97m', 'You lost.')
                        return 0

                if enemy.type != 'drone':
                    self.board = enemy.action(self.board, self.playerSpace)

                    for fireball in enemy.fireballs:
                        if fireball.move(self.board) or fireball.linger <= 0:
                            enemy.fireballs.remove(fireball)

                    for fireball in enemy.fireballs:
                        if fireball.coordinate == self.playerSpace and fireball.hurts:
                            printWithPause(2, '\033[97m', 'You lost.')
                            return 0

                if enemy.coordinate == self.playerSpace or '  i  ' in enemy.tilesSkipped or \
                        self.board[tuple(enemy.coordinate)] == '  i  ':
                    if enemy.type == 'alien warrior' and not [i for i in requiredTiles if i not in visitedSpaces]:
                        printWithPause(2, '\033[97m', 'You won.')
                        return 1

                    else:
                        printWithPause(2, '\033[97m', 'You lost.')
                        return 0

        def playerTurn():
            if '  i  ' not in list(self.board.values()):
                printWithPause(0.5, '\033[97m', 'You lost.')
                return 0

            movement = getInput('\033[97m', 'Where will you go? Use wasd:')

            if movement in list(directionsPerKey.keys()):
                direction = directionsPerKey[movement]
                newLocation = (self.playerSpace[0] + direction[0], self.playerSpace[1] + direction[1])

                if newLocation in self.board.keys() and self.board[newLocation] != ' ||| ':
                    for i in [i for i in list(self.board.keys()) if self.board[i] == '  i  ']:
                        self.board[i] = '     '

                    self.playerSpace = list(newLocation)

                    for enemy in [enemy for enemy in self.board.values() if type(enemy) is movementPuzzleFoe]:
                        if enemy.coordinate == self.playerSpace or '  i  ' in enemy.tilesSkipped:
                            if enemy.type == 'alien warrior' and not \
                                    [i for i in requiredTiles if i not in visitedSpaces] or enemy.type == 'alien pilot':
                                printWithPause(2, '\033[97m', 'You won.')
                                return 1

                            elif enemy.type == 'mysterious figure' and not \
                                    [i for i in requiredTiles if i not in visitedSpaces]:
                                printWithPause(2, '\033[97mYou reached the commander.')
                                printWithPause(2, '\033[97mBut he defeated you.')
                                play('betterOp28No20Chopin.mp3', self, save=False)
                                printWithPause(10, "You died. The alien troops will destroy the world.")

                                if input("Will you play again? y/n:") != 'y':
                                    sys.exit()

                            printWithPause(2, '\033[97m', 'You lost.')
                            return 0

                        for fireball in enemy.fireballs:
                            if fireball.coordinate == self.playerSpace and fireball.hurts:
                                printWithPause(2, '\033[97m', 'You lost.')
                                return 0

                    if self.playerSpace not in visitedSpaces:
                        visitedSpaces.append(self.playerSpace)

                    if mode not in ['alien pilot', 'alien warrior', 'mysterious figure'] and not \
                            [i for i in requiredTiles if i not in visitedSpaces]:
                        printWithPause(2, '\033[97m', 'You won.')
                        return 1

            self.board[tuple(self.playerSpace)] = '  i  '

        while True:
            drawBoard()
            x = playerTurn()

            if x is not None:
                return x

            x = enemyTurns()

            if x is not None:
                return x

    def playTicTacToe(self, mode):
        mode = 'regular' if mode == 'sun priest' else mode
        specialCaseForCommander = True

        if mode == 'drone':
            printWithPause(2, '\033[91mThe drone moves aside to reveal...')
            play("newCommanderTheme.mp3", self, save=False)
            printWithPause(2, 'The alien commander!')
            printWithPause(3, "Taking advantage of your shock, the commander places an O on your board.")

        self.board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        if mode == 'drone':
            initialOCoord = random.choice(['a', 'c']) + random.choice(['1', '1'])
            self.board[initialOCoord] = 'O'

        def drawBoard():
            print('\033[97m', '      1     2     3')
            print('\033[97m', '   ------------------')

            for i in ['a', 'b', 'c']:
                print('\033[97m', f'{i} |  {self.board[f"{i}1"]}  |  {self.board[f"{i}2"]}  |  '
                                  f'{self.board[f"{i}3"]}  |')
                print('\033[97m', '   ------------------')

        def handlePlayerTurn():
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

        def getLines(boardUsed):
            lines = []

            for i in ['a', 'b', 'c']:
                lines.append({f'{i}1': boardUsed[f'{i}1'], f'{i}2': boardUsed[f'{i}2'], f'{i}3': boardUsed[f'{i}3']})

            for i in range(1, 4):
                lines.append({f'a{i}': boardUsed[f'a{i}'], f'b{i}': boardUsed[f'b{i}'], f'c{i}': boardUsed[f'c{i}']})

            lines.append({'a1': boardUsed['a1'], 'b2': boardUsed['b2'], 'c3': boardUsed['c3']})
            lines.append({'c1': boardUsed['c1'], 'b2': boardUsed['b2'], 'a3': boardUsed['a3']})
            return lines

        def handleSpecialCasesForCommander():
            xAndOQty = len([i for i in self.board.values() if i != ' '])
            oppositeCorner = ('a' if initialOCoord[0] == 'c' else 'c') + ('1' if initialOCoord[1] == '3' else '3')
            otherCorners = [initialOCoord[0] + oppositeCorner[1], oppositeCorner[0] + initialOCoord[1]]
            adjacentSpaces = [initialOCoord[0] + '2', 'b' + initialOCoord[1]]
            emptySpaces = [i for i in self.board.keys() if self.board[i] == ' ']
            specialCaseForCommander = False

            match xAndOQty:
                case 1:
                    printWithPause(2, '\033[97mThe commander waits for you to place an X.')
                    specialCaseForCommander = True

                case 2:
                    initialXCoord = [i for i in self.board.keys() if self.board[i] == 'X'][0]

                    if initialXCoord in otherCorners:
                        self.board[oppositeCorner] = 'O'
                        specialCaseForCommander = False

                    elif initialXCoord in adjacentSpaces:
                        self.board['b2'] = 'O'
                        specialCaseForCommander = True
                    
                    elif initialXCoord == 'b2':
                        self.board[random.choice(emptySpaces)] = "O"
                        specialCaseForCommander = False

                    elif initialXCoord == oppositeCorner:
                        self.board[random.choice(otherCorners)] = 'O'
                        specialCaseForCommander = False

                    else:
                        self.board['b2'] = 'O'
                        specialCaseForCommander = False
                    
                case 4:
                    specialCaseForCommander = False
                    lines = getLines(self.board)
                    almostFinishedOLines = [line for line in lines if \
                                            list(line.values()).count('O') == 2 and \
                                            list(line.values()).count(' ')]

                    if almostFinishedOLines:
                        lineFinished = random.choice(almostFinishedOLines)
                        spaceChosen = [point for point in lineFinished.keys() if self.board[point] == ' '][0]
                        self.board[spaceChosen] = "O"

                    else:
                        adjacentXCoord = [i for i in adjacentSpaces if self.board[i] == 'X'][0]
                        chosenSpace = [i for i in otherCorners if i[0] != adjacentXCoord[0] and \
                                       i[1] != adjacentXCoord[1]][0]
                        self.board[chosenSpace] = "O"

            return specialCaseForCommander

        def enemyTurn():
            try:
                if mode in ['regular', 'alien pilot', 'drone']:
                    almostFinishedOLines = [line for line in lines if \
                                            list(line.values()).count('O') == 2 and \
                                            list(line.values()).count(' ')]

                    if mode != 'alien pilot':
                        almostFinishedXLines = [line for line in lines if \
                                                list(line.values()).count('X') == 2 and \
                                                list(line.values()).count(' ')]

                    if almostFinishedOLines:
                        lineFinished = random.choice(almostFinishedOLines)
                        emptySpace = [point for point in lineFinished.keys() if self.board[point] == ' '][0]

                    elif mode != 'alien pilot' and almostFinishedXLines:
                        lineStopped = random.choice(almostFinishedXLines)
                        emptySpace = [point for point in lineStopped.keys() if self.board[point] == ' '][0]

                    else:
                        emptySpace = random.choice([key for key in list(self.board.keys()) if \
                                                    self.board[key] == ' '])

                        if mode == 'drone':
                            availableSpaces = [i for i in self.board.keys() if self.board[i] == ' ']

                            for space in availableSpaces:
                                experimentalBoard = self.board.copy()
                                experimentalBoard[space] = 'O'
                                newLines = getLines(experimentalBoard)
                                newAlmostFinishedOLines = [line for line in newLines if \
                                                           list(line.values()).count('O') == 2 and \
                                                           list(line.values()).count(' ')]
                                newAlmostFinishedXLines = [line for line in newLines if \
                                                           list(line.values()).count('X') == 2 and \
                                                           list(line.values()).count(' ')]

                                if len(newAlmostFinishedOLines) > 1 and not newAlmostFinishedXLines:
                                    emptySpace = space
                                    break


                elif mode == 'alien warrior':
                    emptySpace = random.choice([key for key in list(self.board.keys()) if self.board[key] == ' '])

                else:
                    emptySpace = random.choice([key for key in list(self.board.keys()) if self.board[key] == ' '])

                self.board[emptySpace] = 'O'

            except IndexError:
                return 2

        while True:
            drawBoard()
            handlePlayerTurn()
            lines = getLines(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                if mode == 'drone':
                    printWithPause(2, '\033[97m', 'Before you could place your last X, one of the '
                                                    'commander\'s snipers shot you.')
                    play('betterOp28No20Chopin.mp3', self, save=False)
                    printWithPause(10, "You died. The alien troops will destroy the world.")

                    if input("Will you play again? y/n:") != 'y':
                        sys.exit()

                    return 0

                else:
                    printWithPause(0.5, '\033[97m', 'you won')
                    return 1

            if specialCaseForCommander and mode == 'drone':
                specialCaseForCommander = handleSpecialCasesForCommander()

            elif enemyTurn() == 2:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            lines = getLines(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def experiment(self):
        def getInitializedBoard():
            board = {}

            for i in ['a', 'b', 'c']:
                for j in range(1, 4):
                    board[f'{i}{j}'] = ' '

            return board

        self.board = getInitializedBoard()

        def drawBoard():
            print('\033[97m', '      1     2     3')
            print('\033[97m', '   ------------------')

            for i in ['a', 'b', 'c']:
                print('\033[97m', f'{i} |  {self.board[f"{i}1"]}  |  {self.board[f"{i}2"]}  |  '
                                  f'{self.board[f"{i}3"]}  |')
                print('\033[97m', '   ------------------')

        def handlePlayerTurn():
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

        def getLines(board):
            lines = []

            for i in ['a', 'b', 'c']:
                lines.append({f'{i}1': board[f'{i}1'], f'{i}2': board[f'{i}2'], f'{i}3': board[f'{i}3']})

            for i in range(1, 4):
                lines.append({f'a{i}': board[f'a{i}'], f'b{i}': board[f'b{i}'], f'c{i}': board[f'c{i}']})

            lines.append({'a1': board['a1'], 'b2': board['b2'], 'c3': board['c3']})
            lines.append({'c1': board['c1'], 'b2': board['b2'], 'a3': board['a3']})
            return lines

        def emptySpaces():
            return [i for i in self.board.keys() if self.board[i] == ' ']

        def getAlmostFinishedOLines(lines):
            return [line for line in lines if list(line.values()).count('O') == 2 and list(line.values()).count(' ')]

        def getAlmstFinishedXLines(lines):
            return [line for line in lines if list(line.values()).count('X') == 2 and list(line.values()).count(' ')]

        def enemyTurn():
            lines = getLines(self.board)

            if getAlmostFinishedOLines(lines):
                lineFinished = random.choice(getAlmostFinishedOLines(lines))
                emptySpace = [point for point in lineFinished.keys() if self.board[point] == ' '][0]

            elif getAlmstFinishedXLines(lines):
                lineStopped = random.choice(getAlmstFinishedXLines(lines))
                emptySpace = [point for point in lineStopped.keys() if self.board[point] == ' '][0]

            else:
                paths = {}
                finished = False

                for i in [i for i in self.board.keys() if self.board[i] == ' ']:
                    paths[(i, 'O')] = self.board.copy()
                    paths[(i, 'O')][i] = 'O'

                for j in paths:
                    newPaths = paths.copy()

                    for i in [i for i in paths[j].keys() if paths[j][i] == ' ']:
                        newPaths[j + (i, 'X')] = paths[j].copy()
                        newPaths[j + (i, 'X')][i] = 'X'

                    paths = newPaths.copy()

                while not finished:
                    for j in paths:
                        options = [i for i in paths[j].keys() if paths[j][i] == ' ']
                        newPaths = paths.copy()

                        if options:
                            for i in options:
                                newPaths[j + (i, 'O')] = paths[j].copy()
                                newPaths[j + (i, 'O')][i] = 'O'

                        else:
                            finished = True

                    if not finished:
                        paths = newPaths.copy()

                        for j in paths:
                            options = [i for i in paths[j].keys() if paths[j][i] == ' ']

                            if options:
                                for i in options:
                                    newPaths[j + (i, 'X')] = paths[j].copy()
                                    newPaths[j + (i, 'X')][i] = 'X'

                            else:
                                finished = True

                        paths = newPaths.copy()

                pathsList = list(paths.keys())
                goodPaths = []
                badPaths = []

                for path in [path for path in pathsList if path[-1] == 'O']:
                        hypotheticalLines = getLines(paths[path])

                        if len(getAlmstFinishedXLines(hypotheticalLines)) > 1 and not \
                                getAlmostFinishedOLines(hypotheticalLines):
                            badPaths.append(path)

                        elif len(getAlmostFinishedOLines(hypotheticalLines)) > 1:
                            goodPaths.append(path)

                for path in [path for path in pathsList if path[-1] == 'O']:
                    extensions1 = [route for route in pathsList if len(route) == len(path) + 4 and \
                                  route[:len(path)] == path]

                    code = """
extensions1 = [route for route in pathsList if len(route) == len(path) + 4 and \
                                  route[:len(path)] == path]

for extension1 in extensions1:
    extensions2 = [route for route in pathsList if len(route) == len(path) + 4 and \
                                  route[:len(path)] == path]"""

                    for i in range(8):
                        code += f"""
{'  ' * (i + 1)}for extension{i + 2} in extensions{i + 2}:
    {'  ' * (i + 1)}extensions{i + 3} = [route for route in pathsList if len(route) == len(extension{i + 2}) + 4 and \
                                  {'  ' * (i + 1)}route[:len(extension{i + 2})] == extension{i + 2}]"""

                    for i in range(9):
                        pass

                for badPath in badPaths:
                    for path in [path for path in pathsList if len(path) > len(badPath) and \
                                                               path[:len(badPath)] == badPath]:
                        badPaths.append(path)

                for path in pathsList:
                    if path in goodPaths or path in badPaths:
                        pathsList.remove(path)


                if goodPaths:
                    emptySpace = random.choice(goodPaths)[0]

                elif pathsList:
                    emptySpace = random.choice(pathsList)[0]

                else:
                    printWithPause(3, '\033[95mRealising that you might otherwise beat the commander, '
                                      'he signaled one of his snipers to kill you while you were distracted by the '
                                      'game.')
                    printWithPause(3, '\033[91mThe sniper killed you.')
                    printWithPause(3, 'You died.')

            self.board[emptySpace] = 'O'

        while True:
            drawBoard()
            handlePlayerTurn()
            lines = getLines(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            elif not list(self.board.values()).count(' '):
                print(self.board, 'proTurn')
                printWithPause(0.5, 'You drew.')
                return 2

            enemyTurn()
            lines = getLines(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

            elif not list(self.board.values()).count(' '):
                print(self.board, 'foeTurn')
                printWithPause(0.5, 'You drew.')
                return 2

    def playTicTacToeAgainstTheSunPriest(self):
        self.board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            try:
                almostFinishedXLines = [line for line in lines if \
                                        list(line.values()).count('X') == 2 and \
                                        list(line.values()).count(' ')]
                almostFinishedOLines = [line for line in lines if \
                                        list(line.values()).count('O') == 2 and \
                                        list(line.values()).count(' ')]

                if almostFinishedOLines:
                    lineFinished = random.choice(almostFinishedOLines)
                    emptySpace = [point for point in lineFinished.keys() if self.board[point] == ' '][0]

                elif almostFinishedXLines:
                    lineStopped = random.choice(almostFinishedXLines)
                    emptySpace = [point for point in lineStopped.keys() if self.board[point] == ' '][0]

                else:
                    emptySpace = random.choice([key for key in list(self.board.keys()) if self.board[key] == ' '])

                self.board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            lines = self.getLinesInTicTacToe(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstTheAlienWarrior(self):
        self.board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')
                return 2

            lines = self.getLinesInTicTacToe(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            try:
                emptySpace = random.choice([key for key in list(self.board.keys()) if self.board[key] == ' '])
                self.board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')

            lines = self.getLinesInTicTacToe(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstTheAlienPilot(self):
        self.board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            try:
                almostFinishedOLines = [line for line in lines if \
                                        list(line.values()).count('O') == 2 and \
                                        list(line.values()).count(' ')]

                if almostFinishedOLines:
                    lineFinished = random.choice(almostFinishedOLines)
                    emptySpace = [point for point in lineFinished.keys() if self.board[point] == ' '][0]

                else:
                    emptySpace = random.choice([key for key in list(self.board.keys()) if self.board[key] == ' '])

                self.board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            lines = self.getLinesInTicTacToe(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstADrone(self):
        self.board = {}
        columnNumbers = {'a': 1, 'b': 2, 'c': 3}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        printWithPause(2, '\033[97m', 'You see the drone move aside to reveal...')
        printWithPause(2, '\033[91m', 'The alien commander!')
        printWithPause(2, '\033[97m', 'Taking advantage of your surprise, he takes the first turn.')
        turn = 1

        while True:
            try:
                if turn == 1:
                    emptySpace = random.choice(['a1', 'a3', 'c1', 'c3'])

                else:
                    enemySpots = [tile for tile in list(self.board.keys()) if self.board[tile] == 'O']
                    playerSpots = [tile for tile in list(self.board.keys()) if self.board[tile] == 'O']

                self.board[emptySpace] = 'O'
                turn += 1

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            lines = self.getLinesInTicTacToe(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstAPlayer(self):
        self.board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                self.board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will player 1 take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(self.board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'player 1 won')
                return 1

            if not [list(self.board.values()).count(' ')]:
                printWithPause(0.5, '\033[97m', 'You drew.')

            self.showTicTacToeBoard(self.board)
            spaceTaken = getInput('\033[97m', 'Which available space will player 2 take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if self.board[spaceTaken] == ' ':
                    self.board[spaceTaken] = 'O'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(self.board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'player 2 won')
                return 0

            if not [list(self.board.values()).count(' ')]:
                printWithPause(0.5, '\033[97m', 'You drew.')

    def playMovementPuzzles(self):
        self.board = {}
        self.playerSpace = [4, 8]
        visitedSpaces = [[4, 8]]
        directionsPerKey = {'w': [0, -1], 'a': [-1, 0], 's': [0, 1], 'd': [1, 0]}

        for i in range(9):
            for j in range(9):
                self.board[(i, j)] = '     '

        for i in range(5):
            for j in range(5):
                self.board[(2 * j + 1, 2 * i + 1)] = ' ||| '

        for i in range(5):
            for j in getRandomItemsFromList([h * 2 for h in range(5)], 2):
                self.board[(j, 2 * i + 1)] = ' ||| '

        for i in [0, 2, 4]:
            xCoord = random.randint(0, 8)
            self.board[(xCoord, i)] = movementPuzzleFoe([xCoord, i],
                                                        random.choice(['mage', 'charging', 'basic']), self.board)

        self.board[(4, 8)] = '  i  '
        requiredTiles = []

        for i in range(9):
            requiredTiles.append(random.choice([list(key) for key in self.board.keys() if self.board[key] == '     ' and \
                                                key[1] == i]))

        while True:
            self.showMovementPuzzle(self.board, visitedSpaces, requiredTiles)

            for key in [key for key in self.board.keys() if type(self.board[key]) is movementPuzzleFoe]:
                enemy = self.board[key]
                self.board = enemy.action(self.board, self.playerSpace)

                for fireball in enemy.fireballs:
                    if fireball.move(self.board):
                        enemy.fireballs.remove(fireball)

            movement = getInput('\033[97m', 'Where will you go? Use wasd:')

            for i in range(200):
                print(' ')

            if movement in list(directionsPerKey.keys()):
                direction = directionsPerKey[movement]
                newLocation = (self.playerSpace[0] + direction[0], self.playerSpace[1] + direction[1])

                if newLocation in self.board.keys() and self.board[newLocation] != ' ||| ':
                    for i in [i for i in list(self.board.keys()) if self.board[i] == '  i  ']:
                        self.board[i] = '     '

                    self.playerSpace = list(newLocation)

                    if self.playerSpace not in visitedSpaces:
                        visitedSpaces.append(self.playerSpace)

            for key in [key for key in self.board.keys() if type(self.board[key]) is movementPuzzleFoe]:
                enemy = self.board[key]

                if enemy.coordinate == self.playerSpace or '  i  ' in enemy.tilesSkipped:
                    printWithPause(2, '\033[97m', 'You lost.')
                    return 0

                for fireball in enemy.fireballs:
                    if fireball.coordinate == self.playerSpace:
                        printWithPause(2, '\033[97m', 'You lost.')
                        return 0

            self.board[tuple(self.playerSpace)] = '  i  '

            if not [item for item in requiredTiles if not item in visitedSpaces]:
                printWithPause(2, '\033[97m', 'You won.')
                return 1

    def playGoblinGame(self, mode):
        if mode == 'unknown character':
            printWithPause(2, "\033[91mThe unknown character removes their mask. "
                              "You see that they are actually...")
            play("newCommanderTheme.mp3", self, save=False)
            printWithPause(2, "The alien commander!")

        print('\033[97m')
        doors = {}
        self.warriorFound = 0
        self.highestFootprintNumberFound = 0

        class door:
            def __init__(self, coordinate, number=None):
                self.coordinate = coordinate.copy()
                self.lastCoordinate = None
                self.hasGoblin = 0
                self.strings = ['------ ', '|      ', '|      ', '|      ', '|      ', '| |-|  ']
                self.number = number
                self.showsNumber = 1

            def getStrings(self):
                strings = []
                movement = [self.coordinate[0] - self.lastCoordinate[0], self.coordinate[1] - self.lastCoordinate[1]]

                if movement[1] > 0:
                    strings += ['|  |   ', '|  v   ', f'|  {movement[1]}   ']

                if movement[0] > 0:
                    strings += [f'| -->{movement[0]} ']

                elif movement[0] < 0:
                    strings += [f'|{-movement[0]}<--  ']

                if movement[1] < 0:
                    strings += [f'|  {-movement[1]}   ', '|  ^   ', '|  |   ']

                strings = ['-------'] + [f'|{(self.coordinate[0] + 1, self.coordinate[1] + 1)}'] + \
                          ['|      ' for i in range(4 - len(strings))] + strings

                if mode == 'unknown character' and self.showsNumber:
                    strings.append(f'|  {self.number}{" " * (4 - len(str(self.number)))}')

                strings += ['|\033[93m |-|  \033[97m'] if mode == 'sun priest' and self.hasGoblin else ['| |-|  ']
                return strings

        def shuffleDoors():
            shuffledDoors = list(doors.values())
            random.shuffle(shuffledDoors)
            returnedDoors = {}

            for i in range(6):
                for j in range(2):
                    doorAdded = copy.deepcopy(shuffledDoors[j * 6 + i])
                    returnedDoors[(i, j)] = doorAdded
                    doorAdded.lastCoordinate = doorAdded.coordinate.copy()
                    doorAdded.coordinate = [i, j].copy()

            return returnedDoors

        def drawBoard():
            for j in range(2):
                for h in range(7):
                    text = ''

                    for i in range(6):
                        text += doors[(i, j)].getStrings()[h]

                    if j > 0 or h > 0:
                        text += '|'

                    else:
                        text += '-'

                    print(text)

            if mode == 'regular':
                printWithPause(7, '-------------------------------------------')

            else:
                print('-------------------------------------------')

        def guessTheDoor():
            guess = getInput('\033[97m', 'What door will you open? Enter the coordinate:')
            wrong = True

            try:
                guess = eval(guess)
                guess = (guess[0] - 1, guess[1] - 1)

                if mode != 'unknown character':
                    if doors[guess].hasGoblin:
                        if mode == 'alien warrior' and not self.warriorFound:
                            wrong = False
                            self.warriorFound = True
                            warriorCoordinate = [i.coordinate for i in doors.values() if i.hasGoblin][0]
                            printWithPause(1, f"The alien warrior got away. Find him again to win. He is at "
                                              f"{(warriorCoordinate[0] + 1, warriorCoordinate[1] + 1)}. The doors have "
                                              f"been shuffled again.")

                        else:
                            printWithPause(0.5, 'You won.')
                            return 1

                else:
                    if doors[guess].number == self.highestFootprintNumberFound + 1:
                        self.highestFootprintNumberFound = doors[guess].number
                        wrong = False

                        if self.highestFootprintNumberFound == 12:
                            printWithPause(3, 'You found what appears to be the alien commander.')
                            printWithPause(3, 'But you actually found a decoy.')
                            printWithPause(3, 'The decoy exploded, killing you.')
                            printWithPause(3, 'You lost.')
                            return 0

                    else:
                        printWithPause(2, 'You lost.')
                        return 0

            except:
                pass

            if wrong:
                printWithPause(0.5, 'Try again.')

            return shuffleDoors()

        numbers = [i for i in range(1, 13)]
        random.shuffle(numbers)

        for i in range(6):
            for j in range(2):
                doors[(i, j)] = door([i, j], number=numbers[6 * j + i])

        rightDoor = random.choice(list(doors.values()))
        rightDoor.hasGoblin = 1

        if mode == 'regular':
            printWithPause(2, f'The goblin is behind the door that has coordinate '
                              f'{(rightDoor.coordinate[0] + 1, rightDoor.coordinate[1] + 1)}.')

            for i in range(5):
                doors = shuffleDoors()
                drawBoard()

        elif mode == 'unknown character':
            doors = shuffleDoors()
            drawBoard()

            for i in doors.values():
                i.showsNumber = 0

            for i in range(15):
                doors = shuffleDoors()
                drawBoard()

        else:
            doors = shuffleDoors()
            drawBoard()

        while True:
            x = guessTheDoor()
            doors = x

            if type(x) == int:
                return x

            drawBoard()

    def playWhereIsWaldo(self, mode):
        self.board = {}
        colors = [f'\033[3{i}m' for i in range(1, 8)] + [f'\033[9{i}m' for i in range(1, 7)]
        characters = [i for i in ('`1234567890-=qwertyuop[]asdfghjkl;zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}'
                                  '|ASDFGHJKL:"ZXCVBNM<>?`™£¢∞§¶•ªº–≠œ∑´®†¥¨ˆøπ“‘«åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥µ')]
        horizontalCharsStr = 'abcdefghijklnmopqrstvuwyxz'
        horizontalCharsDict = dict(zip(list('abcdefghijklnmopqrstvuwyxz'), list(range(26))))

        for i in range(26):
            for j in range(10):
                self.board[(i, j)] = f'{random.choice(colors)}{random.choice(characters)}'

        self.board[random.choice(list(self.board.keys()))] = '\033[91mi'

        def showBoard():
            print(f'\033[97m {horizontalCharsStr}')
            charsAvailable = characters.copy()

            for i in range(10):
                message = ''

                for j in range(26):
                    message += self.board[(j, i)]

                print(f'\033[97m{i}{message}')

        def enterCoord():
            guessHor = input('Enter the first coordinate of the red character "i".')
            guessVer = input('Enter the second coordinate of the red character "i".')

            try:
                if self.board[(horizontalCharsDict[guessHor], int(guessVer))] == '\033[91mi':
                    printWithPause(1, '\033[97mYou are correct.')
                    return 1

                printWithPause(1, '\033[97mYou are wrong.')
                return 0

            except Exception as E:
                    printWithPause(1, '\033[97mYour input was invalid.')
                    print(E)
                    return 0

        showBoard()

        while True:
            if enterCoord():
                return 1

            showBoard()

    def tryToOpenBox(self):
        if self.lockedBoxPuzzles and self.lockedBoxPuzzles[0]('regular') == 1:
            self.lockedBoxPuzzles.pop(0)
            printWithPause(1, '\033[96m', 'A lock opened in your box.')

            if not self.lockedBoxPuzzles:
                printWithPause(2, '\033[96m', 'You opened your box.')
                printWithPause(2, '\033[96m', 'You found 5 potions in your box.')
                self.potions += 5

    def handlePuzzleMenu(self, file):
        action = None
        proceed = 0

        while not proceed:
            action = getInput('\033[96m', "Type 'e' to exit, 't' to play tic tac toe, 'g' to play the "
                                          "goblin game, 'm' to play the movement puzzle, or "
                                          "'w' to play where's Waldstein:")

            if action == 'e':
                if self.handleTitleScreen(file):
                    play('The War.mp3', self, save=False)
                    return 1

            elif action == 't':
                action = None
                modesPerAction = {'1': 'drone', '2': 'alien pilot', '3': 'alien warrior', '4': 'sun priest'}

                while action not in list(modesPerAction.keys()):
                    modesPerAction = {'1': 'drone', '2': 'alien pilot', '3': 'alien warrior', '4': 'sun priest'}
                    action = getInput("\033[96mWho will you face in tic tac toe? Type 'e' to exit,'1' to face a drone, "
                                      "'2' to face the alien pilot, '3' to face the alien warrior, or '4' to face the "
                                      "sun priest.")

                    if action == 'e':
                        self.handlePuzzleMenu(file)

                self.playTicTacToe(modesPerAction[action])

            elif action == 'g':
                action = None
                modesPerAction = {'1': 'unknown character', '2': 'alien pilot', '3': 'alien warrior', '4': 'sun priest'}

                while action not in list(modesPerAction.keys()):
                    modesPerAction = {'1': 'unknown character', '2': 'alien pilot', '3': 'alien warrior',
                                      '4': 'sun priest'}
                    action = getInput("\033[96mWho will you face in the goblin game? Type 'e' to exit,'1' to face an "
                                      "unknown character, '2' to face the alien pilot, '3' to face the alien warrior, "
                                      "or '4' to face the sun priest.")

                    if action == 'e':
                        self.handlePuzzleMenu(file)

                self.playGoblinGame(modesPerAction[action])

            elif action == 'm':
                action = None
                modesPerAction = {'1': 'mysterious figure', '2': 'alien pilot', '3': 'alien warrior', '4': 'sun priest'}

                while action not in list(modesPerAction.keys()):
                    modesPerAction = {'1': 'mysterious figure', '2': 'alien pilot', '3': 'alien warrior',
                                      '4': 'sun priest'}
                    action = getInput("\033[96mWho will you face in the movement game? Type 'e' to exit,'1' to face a "
                                      "mysterious figure, '2' to face the alien pilot, '3' to face the alien warrior, "
                                      "or '4' to face the sun priest.")

                    if action == 'e':
                        self.handlePuzzleMenu(file)

                self.playMovementPuzzle(modesPerAction[action])

            elif action == 'w':
                self.playWhereIsWaldo('')

        play('The War.mp3', self, save=False)

    def handleTitleScreen(self, file):
        action = None

        while action != 'y':
            action = getInput('\033[96m', "Type 'y' to play, 'b' to view your bestiary, 'e' to exit the game, "
                                          "'s' to delete a save, or 'p' to play a game against an enemy:")

            if action == 'y':
                return 1

            if action == 'b':
                self.showBestiary()

            elif action == 'e':
                sys.exit()

            elif action == 's':
                fileDeleted = getInput('\033[96m', 'What file will you delete:')

                if getInput('\033[96m', 'Type "delete" to delete your file:') == 'delete':
                    try:
                        os.remove(f'playerSave{fileDeleted}.pickle')

                        if fileDeleted == f'{file}':
                            printWithPause(1, '\033[96m', 'Your file was deleted. Reload the game to '
                                                          'continue.')
                            sys.exit()

                    except FileNotFoundError:
                        pass

            elif action == 'p':
                if self.handlePuzzleMenu(file):
                    return 1

    def getUpdate(self):
        example = player()

        for i in list(vars(example).keys()):
            if not hasattr(self, i):
                exec(f'self.{i} = example.{i}')