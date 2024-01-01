import random

from definitions import (lesser, printWithPause, getReducedDamage, percentChance, getTarget,
                         getListOfThingsWithCommas)
from variables import oneTimeUseItems


class player:
    def __init__(self):
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

    def showHp(self):
        hpDashCount = int(self.hp / 10)
        emptySpaceCount = int(self.maxHp / 10 - hpDashCount)
        printWithPause(f'You have {self.hp} hit points and {self.potions} potions.')
        printWithPause(f'[{"_" * hpDashCount}{" " * emptySpaceCount}]')
        printWithPause(self.inventory)

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
                                                                     and foe.hp > 0]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0])
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

                        if self.inventory.count('baton'):
                            enemy.stun = self.inventory.count('baton')
                            printWithPause(f'You hit {enemy.getPrintName()} with your baton, '
                                           f'stunning them for {enemy.stun} turns.')

                    enemy.hp -= damageInflicted

                    if enemy.gunWeakness:
                        damageInflicted = getReducedDamage(20, enemy)

                        for i in range(self.inventory.count('gun')):
                            printWithPause(f'You shot {enemy.getPrintName()}, '
                                           f'inflicting {damageInflicted} damage.')
                            enemy.hp -= damageInflicted

            except AttributeError:
                pass

        else:
            printWithPause('You are in an empty room.')

    def scan(self, enemies):
        printWithPause('The enemies in your room are:')

        for enemy in enemies:
            printWithPause(f'{enemy.getPrintName()} with {enemy.hp} hp')
            enemy.scanned = 1

    def knifeAttack(self, enemies):
        targetId = input("Enter the id number of the foe you want to stab with "
                         "your knife or 'r' to stab a random foe:")
        enemy = getTarget(enemies, targetId)

        try:
            if enemy.type in ['alien priest', 'sun priest'] and [foe for foe in enemies if
                                                                 foe.type == 'alien worshipper'
                                                                 and foe.hp > 0]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type == 'alien worshipper'
                                             and foe.hp > 0])
                attackedFoe.hp = 0
                printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

            else:
                damageInflicted = getReducedDamage(5, enemy)
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
                                                                     and foe.hp > 0]:
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0])
                    attackedFoe.hp = 0
                    printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

                else:
                    damageInflicted = getReducedDamage(5, enemy)
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
                                                                 and foe.hp > 0]:
                attackedFoe = random.choice([foe for foe in enemies if
                                             foe.type == 'alien worshipper'
                                             and foe.hp > 0])
                attackedFoe.hp = 0
                printWithPause(f'{attackedFoe.getPrintName()} got in the way of your attack.')

            else:
                damageInflicted = getReducedDamage(10, enemy)
                printWithPause(f'You hit {enemy.getPrintName()} '
                               f'with your nunchucks, inflicting {damageInflicted} damage.')
                enemy.hp -= damageInflicted
                enemy.nunchuckDebuff = 1

                for i in range(self.inventory.count('gun')):
                    printWithPause(f'You shot {enemy.getPrintName()}, '
                                   f'inflicting {damageInflicted} damage.')
                    enemy.hp -= damageInflicted

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

                else:
                    printWithPause(f'You hit {enemy.getPrintName()} with your solution, '
                                   f'causing them to be possessed by you..')
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
        if 'throwing knife' in self.inventory:
            targetId = input('Enter the id number of the foe you want to throw your vial '
                             "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                printWithPause(f'You hit {enemy.getPrintName()} with your vial, poisoning them.')
                enemy.poisonDamage = 15
                self.inventory.remove('throwing knife')

            except AttributeError:
                pass

        else:
            printWithPause('You do not have a vial of poison.')

    def useOneTimeUseItem(self, enemies):
        printWithPause('Your one time use items are:')

        for item in self.inventory:
            if item in oneTimeUseItems:
                printWithPause(item)

        itemUsed = input(f'What item will you use:')

        if itemUsed == 'solution':
            self.useSolution(enemies)

        elif itemUsed == 'throwing knife':
            self.useThrowingKnife(enemies)

        elif itemUsed == 'stun grenade':
            self.useStunGrenade(enemies)

        elif itemUsed == 'vial of poison':
            self.useVialOfPoison(enemies)

    def usePotion(self):
        if self.potions > 0:
            oldHp = self.hp
            self.heal(50)
            printWithPause(f'You used a potion. You regained {self.hp - oldHp} hit points.')
            self.potions -= 1

        else:
            printWithPause('You do not have a potion.')

    def updateStats(self):
        self.attack = 10 + self.inventory.count('sword') * 5
        self.maxHp = self.initialHp + self.inventory.count('armor') * 15

    def actions(self, enemies, level):
        self.blocking = 0
        self.damageReduction = 0

        if self.stun:
            self.stun = 0
            printWithPause('You are stunned.')

        else:
            actionList = ["Type 'a' to perform a basic attack", "'s' to scan"]

            if self.potions:
                actionList.append("'h' to use a potion")

            if [item for item in self.inventory if item in oneTimeUseItems]:
                actionList.append("'c' to use a one time use item")

            if 'shield' in self.inventory:
                actionList.append("'b' to block")

            if 'nunchucks' in self.inventory:
                actionList.append("'n' to use your nunchucks")

            if not [enemy for enemy in enemies if not enemy.possessed] and level < 4:
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

            elif (action == 'y' and not [enemy for enemy in enemies if not enemy.possessed]
                  and level < 4):
                return 1

            for i in range(self.inventory.count('knife')):
                if [enemy for enemy in enemies if enemy.hp > 0]:
                    self.knifeAttack(enemies)

            for i in range(self.inventory.count('butterfly knife')):
                if [enemy for enemy in enemies if enemy.hp > 0]:
                    self.butterflyKnifeAttack(enemies)

    def performNecessaryFunctions(self, enemies, level):
        self.showHp()
        self.getRegen()
        self.updateStats()

        if self.actions(enemies, level):
            return 1