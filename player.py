import random

from definitions import (lesser, printWithPause, getReducedDamage, percentChance, getTarget,
                         getListOfThingsWithCommas, greater)
from variables import oneTimeUseItems


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
        self.sunPriestSpawned = 0
        self.sunPriestSpotted = 0
        self.standardAttack = 10
        self.temporaryAttack = 0
        self.temporaryAttackDuration = 0
        self.hasReachedLevelFour = 0
        self.hasReachedLevelTwo = 0

        for key in extra.keys():
            exec(f'self.{key} = extra[key]')

    def showHp(self):
        hpDashCount = int(self.hp / 10)
        emptySpaceCount = int(self.maxHp / 10 - hpDashCount)
        upgradeInventory = [item for item in self.inventory if item not in oneTimeUseItems]
        oneTimeItemInventory = [item for item in self.inventory if item in oneTimeUseItems]
        printWithPause(f'You have {self.hp} hit points and {self.potions} potions.')
        printWithPause(f'[{"_" * hpDashCount}{" " * emptySpaceCount}]')
        printWithPause(f"Upgrade items: {upgradeInventory}")

        if oneTimeItemInventory:
            printWithPause(f"One time use items: {oneTimeItemInventory}")

        if self.souls:
            printWithPause(f"Souls: {[enemy.getPrintName() for enemy in self.souls]}")

    def heal(self, amount):
        self.hp = lesser(self.hp + amount, self.maxHp)

    def getRegen(self):
        for i in range(self.inventory.count('regen')):
            oldHp = self.hp
            self.heal(3)
            printWithPause(f'You regained {self.hp - oldHp} hit points.')

    def basicAttack(self, enemies):
        if enemies:
            targetId = input("Enter the id number of the foe you want to attack or "
                             "'r' to attack a random foe:")

            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                          foe.type == 'alien protector']:
                    printWithPause(f'You hit {enemy.getPrintName()}, but they were immune.')

                else:
                    if percentChance(50):
                        damageInflicted = getReducedDamage(self.attack, enemy)
                        printWithPause(f'You hit {enemy.getPrintName()}, inflicting '
                                       f'{damageInflicted} '
                                       f'damage.')

                    else:
                        damageInflicted = getReducedDamage(self.attack, enemy) * 2
                        printWithPause(f'You hit {enemy.getPrintName()} with a critical '
                                       f'attack, inflicting {damageInflicted} damage.')

                    enemy.hp -= damageInflicted

                    if 'baton' in self.inventory:
                        enemy.beHitByBaton()

                    if enemy.gunWeakness and 'gun' in self.inventory:
                        if enemy.type == 'alien commander' and [protector for protector in
                                                                enemies if protector.type
                                                                == 'alien protector']:
                            printWithPause(f'You shot {enemy.getPrintName()}, but they were '
                                           f'immune.')

                        else:
                            damageInflicted = getReducedDamage(self.attack / 2, enemy)

                            for i in range(self.inventory.count('gun')):
                                printWithPause(f'You shot {enemy.getPrintName()}, '
                                               f'inflicting {damageInflicted} damage.')
                                enemy.hp -= damageInflicted

                            enemy.bleedingDamageFromGun = 3
                            enemy.turnsOfBleedingFromGun = 3

            except AttributeError:
                pass

        else:
            printWithPause('You are in an empty room.')

    def scan(self, enemies):
        printWithPause('The enemies in your room are:')

        if 'radio' in self.inventory:
            for enemy in enemies:
                enemy.scanned = 1
                printWithPause(f'   {enemy.fullName} with {enemy.hp} hp')

        else:
            for enemy in enemies:
                printWithPause(f'   {enemy.getPrintName()} with {enemy.hp} hp')
                enemy.scanned = 1

    def knifeAttack(self, enemies):
        targetId = input("Enter the id number of the foe you want to stab with "
                         "your knife or 'r' to stab a random foe:")
        enemy = getTarget(enemies, targetId)

        try:
            if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                 foe.type == 'alien worshipper'
                                                                 and foe.hp > 0 and foe.possessed ==
                                                                 enemy.possessed]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type == 'alien worshipper'
                                             and foe.hp > 0 and foe.possessed ==
                                             enemy.possessed])
                attackedFoe.hp = 0
                printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

            elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                      foe.type == 'alien protector']:
                printWithPause(f'You stabbed {enemy.getPrintName()}, but they were immune.')

            else:
                damageInflicted = getReducedDamage(self.attack / 2, enemy)
                printWithPause(f'You stabbed {enemy.getPrintName()} '
                               f'with your knife, inflicting '
                               f'{damageInflicted} damage.')
                enemy.hp -= damageInflicted

        except AttributeError:
            pass

    def butterflyKnifeAttack(self, enemies):
        for i in range(2):
            targetId = input("Enter the id number of a foe you want to slash with "
                             "your butterfly knife or 'r' to slash a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                          foe.type == 'alien protector']:
                    printWithPause(f'You slashed {enemy.getPrintName()}, but they were immune.')

                else:
                    damageInflicted = getReducedDamage(self.attack / 2, enemy)
                    printWithPause(f'You slashed {enemy.getPrintName()} '
                                   f'with your butterfly knife, inflicting '
                                   f'{damageInflicted} damage.')
                    enemy.hp -= damageInflicted

            except AttributeError:
                pass

    def useNunchucks(self, enemies):
        targetId = input("Enter the id number of the foe you want to hit with your nunchucks "
                         "or 'r' to hit a random foe.")
        enemy = getTarget(enemies, targetId)

        try:
            if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                 foe.type == 'alien worshipper'
                                                                 and foe.hp > 0 and foe.possessed ==
                                                                 enemy.possessed]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type == 'alien worshipper'
                                             and foe.hp > 0 and foe.possessed ==
                                             enemy.possessed])
                attackedFoe.hp = 0
                printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

            elif enemy.type == 'alien commander' and [foe for foe in enemies if enemy.type == 'alien protector']:
                printWithPause(f'You hit {enemy.getPrintName()}, but they were immune.')

            else:
                damageInflicted = getReducedDamage(10, enemy)
                printWithPause(f'You hit {enemy.getPrintName()} '
                               f'with your nunchucks, inflicting {damageInflicted} damage.')
                enemy.hp -= damageInflicted
                enemy.nunchuckDebuff = 1

        except AttributeError:
            pass

    def useSolution(self, enemies):
        if 'solution' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your solution at '
                             'or 'r' to target a random foe:')
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien pilot', 'alien warrior', 'sun priest']:
                    printWithPause(f'{enemy.getPrintName()} is immune to your solution.')

                if enemy.type == 'alien priest' and [foe for foe in enemies if foe.type == 'alien worshipper'
                                                     and foe.hp > 0 and foe.possessed ==
                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your solution.')

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your solution, '
                                   f'causing them to be possessed by you.')
                    enemy.possessed = 1
                    self.inventory.remove('solution')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a solution.')

    def useThrowingKnife(self, enemies):
        if 'throwing knife' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your knife '
                             "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your knife, poisoning them.')
                    enemy.poisonDamage = lesser(5, enemy.poisonDamage)

                self.inventory.remove('throwing knife')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a throwing knife.')

    def useStunGrenade(self, enemies):
        if 'stun grenade' in self.inventory:
            for enemy in enemies:
                enemy.stun = 2
                printWithPause(f'You stunned {enemy.getPrintName()} with your stun grenade.')

            self.inventory.remove('stun grenade')

        else:
            printWithPause('You do not have a stun grenade.')

    def useVialOfPoison(self, enemies):
        if 'vial of poison' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your vial '
                             "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your vial, poisoning them.')
                    enemy.poisonDamage = 15

                self.inventory.remove('vial of poison')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a vial of poison.')

    def useSerratedKnife(self, enemies):
        if 'serrated knife' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your serrated knife '
                             "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your knife, causing them to bleed.')
                    enemy.bleedingDamage = 5

                self.inventory.remove('serrated knife')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a serrated knife.')

    def useCombustibleLemon(self, enemies):
        if 'combustible lemon' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your combustible lemon '
                             "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                     foe.type == 'alien worshipper'
                                                                     and foe.hp > 0 and foe.possessed ==
                                                                     enemy.possessed]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your combustible lemon, poisoning them. '
                                   f'The lemon combusted, burning {enemy.getPrintName()}.', 2)
                    enemy.poisonDamage = 15
                    enemy.burnDamage = 15

                self.inventory.remove('combustible lemon')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a combustible lemon.')

    def useOneTimeUseItem(self, enemies):
        printWithPause('Your one time use items are:')

        for item in self.inventory:
            if item in oneTimeUseItems:
                printWithPause(f'   {item}')

        itemUsed = input(f'What item will you use:')

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
        if self.potions > 0:
            oldHp = self.hp
            self.heal(50)
            printWithPause(f'You used a potion. You regained {self.hp - oldHp} hit points.')
            self.potions -= 1

        else:
            printWithPause('You do not have a potion.')

    def updateStats(self):
        self.standardAttack = 10 + self.inventory.count('sword') * 5
        self.maxHp = self.initialHp + self.inventory.count('armor') * 15
        self.attack = self.temporaryAttack + self.standardAttack

        if self.temporaryAttackDuration <= 0:
            self.temporaryAttack = 0

        else:
            self.temporaryAttackDuration -= 1

    def releaseSoul(self):
        soulId = input("Type the id of the soul you want to release:")
        soul = [enemy for enemy in self.souls if enemy.number == int(soulId)][0]
        self.souls.remove(soul)
        self.newFoes.append(soul)
        printWithPause(f"You released the soul of {soul.getPrintName()}.")

    def useSacrificialDagger(self):
        hpSacrificed = int(input('How much hp will you turn into extra temporary attack:'))

        if hpSacrificed > 0:
            printWithPause(f'You got {hpSacrificed} extra temporary attack and lost {hpSacrificed} hp.')
            self.temporaryAttackDuration = 3
            self.temporaryAttack = hpSacrificed
            self.hp -= hpSacrificed

    def getCustomInput(self):
        try:
            exec(input('What will you do:'))

        except Exception as error:
            printWithPause(f'Your command raised an error saying, "{error}."')

        if input('Would you like to exit the terminal for custom inputs? y/n:') != 'y':
            self.getCustomInput()

    def actions(self, enemies, level):
        self.blocking = 0
        self.damageReduction = 0

        if not self.sunPriestSpotted and self.enemiesKilledInLevelFour >= 15:
            self.sunPriestSpotted = 1
            printWithPause("You have made a gap in the mob surrounding you. Through the gap, you "
                           "see a cathedral in the distance.", 5)

        if self.stun:
            self.stun = 0
            printWithPause('You are stunned.')

        else:
            if 'sacrificial dagger' in self.inventory and self.temporaryAttackDuration <= 0 \
                    and input("Will you use your sacrificial dagger? y/n:") == 'y':
                self.useSacrificialDagger()

            self.updateStats()
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

            if not [enemy for enemy in enemies if not enemy.possessed] and level < 4 or (self.enemiesKilledInLevelFour
                                                                                         >= 15
                                                                                         and not self.sunPriestSpawned):
                actionList.append("'y' to progress to the next area")

            action = input(getListOfThingsWithCommas('or', actionList, ':'))

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

            elif action == 'y' and (not [enemy for enemy in enemies if not enemy.possessed]
                                    and level < 4 or self.enemiesKilledInLevelFour >= 15):
                return 1

            elif action == 'other':
                self.getCustomInput()

            for i in range(self.inventory.count('knife')):
                if [enemy for enemy in enemies if enemy.hp > 0]:
                    self.knifeAttack(enemies)

            for i in range(self.inventory.count('butterfly knife')):
                if [enemy for enemy in enemies if enemy.hp > 0]:
                    self.butterflyKnifeAttack(enemies)

    def performNecessaryFunctions(self, enemies, level):
        self.showHp()
        self.getRegen()

        if self.actions(enemies, level):
            return 1
