import random
import os

from definitions import (lesser, printWithPause, getReducedDamage, percentChance, getTarget,
                         getListOfThingsWithCommas, greater, getInput)
from variables import oneTimeUseItems
from drone import drone


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
        self.isDrone = 0
        self.poisonDamage = 0
        self.turnsOfPoisonDamage = 0
        self.bleedingDamage = 0
        self.turnsOfBleedingDamage = 0
        self.burningDamage = 0
        self.turnsOfBurningDamage = 0

        for key in extra.keys():
            exec(f'self.{key} = extra[key]')

    def showHp(self):
        hpDashCount = int(self.hp / 10)
        emptySpaceCount = int(self.maxHp / 10 - hpDashCount)
        upgradeInventory = [item for item in self.inventory if item not in oneTimeUseItems]
        oneTimeItemInventory = [item for item in self.inventory if item in oneTimeUseItems]
        printWithPause(0.5, '\033[96m', f'You have {self.hp} hit points and {self.potions} potions.')
        printWithPause(0.5, '\033[00m', '[', '\033[31m', f'{"_" * hpDashCount}{" " * emptySpaceCount}',
                       '\033[00m', ']')
        printWithPause(0.5, '\033[96m', "Upgrade items: ", '\033[00m', f"{upgradeInventory}")

        if oneTimeItemInventory:
            printWithPause(0.5, '\033[96m', "One time use items: ", '\033[00m', f"{oneTimeItemInventory}")

        if self.souls:
            printWithPause(0.5, '\033[96m', "Souls: ", '\033[00m', f"{[enemy.fullName for enemy
                                                                       in self.souls]}")

    def heal(self, amount):
        self.hp = lesser(self.hp + amount, self.maxHp)

    def getRegen(self):
        for i in range(self.inventory.count('regen')):
            oldHp = self.hp
            self.heal(3)
            printWithPause(0.5, '\033[96m', f'You regained {self.hp - oldHp} hit points.')

    def basicAttack(self, enemies):
        if enemies:
            targetId = getInput('\033[96m', "Enter the id number of the foe you want to attack or "
                                            "'r' to attack a random foe:")

            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
                        damageInflicted = getReducedDamage(self.attack, enemy)
                        printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()}, inflicting '
                                                        f'{damageInflicted} '
                                                        f'damage.')

                    else:
                        damageInflicted = getReducedDamage(self.attack, enemy) * 2
                        printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with a critical '
                                                        f'attack, inflicting {damageInflicted} damage.')

                    enemy.hp -= damageInflicted

                    if enemy.twirlingNunchucks:
                        self.hp -= self.attack
                        printWithPause(0.5, '\033[31m', f'{enemy.getPrintName()} deflected your attack '
                                                        f'with their nunchucks, inflicting {damageInflicted} damage '
                                                        f'to you.')

                    if 'baton' in self.inventory:
                        enemy.beHitByBaton()

                    if enemy.gunWeakness and 'gun' in self.inventory:
                        if enemy.type == 'alien commander' and [protector for protector in
                                                                enemies if protector.type
                                                                == 'alien protector']:
                            printWithPause(0.5, '\033[93m', f'You shot {enemy.getPrintName()}, but they '
                                                            f'were immune.')

                        else:
                            damageInflicted = getReducedDamage(self.attack * 3 / 4, enemy)

                            if enemy.twirlingNunchucks:
                                for i in range(self.inventory.count('gun')):
                                    printWithPause(0.5, '\033[31m', f'You shot at {enemy.getPrintName()}, '
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

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You are in an empty room.')

    def scan(self, enemies):
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
        targetId = getInput('\033[96m', "Enter the id number of the foe you want to stab with "
                                        "your knife or 'r' to stab a random foe:")
        enemy = getTarget(enemies, targetId)

        try:
            if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                 foe.type in ['alien worshipper', 'alien cardinal']
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
                    printWithPause(0.5, '\033[31m', f'{enemy.getPrintName()} deflected your stab '
                                                    f'with their nunchucks, inflicting {damageInflicted} damage '
                                                    f'to you.')

        except AttributeError:
            pass

    def butterflyKnifeAttack(self, enemies):
        for i in range(2):
            targetId = getInput('\033[96m', "Enter the id number of a foe you want to slash with "
                                            "your butterfly knife or 'r' to slash a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
                    damageInflicted = getReducedDamage(self.attack / 2, enemy)
                    printWithPause(0.5, '\033[93m', f'You slashed {enemy.getPrintName()} '
                                                    f'with your butterfly knife, inflicting '
                                                    f'{damageInflicted} damage.')
                    enemy.hp -= damageInflicted

                    if enemy.twirlingNunchucks:
                        self.hp -= self.attack / 2
                        printWithPause(0.5, '\033[31m', f'{enemy.getPrintName()} deflected your slash '
                                                        f'with their nunchucks, inflicting {damageInflicted} damage '
                                                        f'to you.')

            except AttributeError:
                pass

    def useNunchucks(self, enemies):
        targetId = getInput('\033[96m', "Enter the id number of the foe you want to hit with your nunchucks "
                                        "or 'r' to hit a random foe.")
        enemy = getTarget(enemies, targetId)

        try:
            if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                 foe.type in ['alien worshipper', 'alien cardinal']
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
                    printWithPause(0.5, '\033[31m', f'{enemy.getPrintName()} deflected your attack '
                                                    f'with their nunchucks, inflicting 10 damage '
                                                    f'to you.')

        except AttributeError:
            pass

    def useSolution(self, enemies):
        if 'solution' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe you want to throw your solution at '
                                            "or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

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
        if 'throwing knife' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe you want to throw your knife '
                                            "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your throwing knife back at you.')
                    printWithPause(0.5, '\033[31m', 'You got poisoned.')
                    self.poisonDamage = greater(self.poisonDamage, 5)
                    self.turnsOfPoisonDamage = 10
                    self.inventory.remove('throwing knife')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
        if 'stun grenade' in self.inventory:
            for enemy in [enemy for enemy in enemies if not enemy.possessed]:
                enemy.stun = 2
                printWithPause(0.5, '\033[96m', f'You stunned {enemy.getPrintName()} with your '
                                                f'stun grenade.')

            self.inventory.remove('stun grenade')

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a stun grenade.')

    def useVialOfPoison(self, enemies):
        if 'vial of poison' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe you want to throw your vial '
                                            "at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} hit your vial of poison '
                                                    f'with their nunchucks. Your vial of poison shattered, covering '
                                                    f'the nun with poison. The nun is now poisoned')
                    enemy.poisonDamage = 15

                elif enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
        if 'serrated knife' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe you want to throw your '
                                            "serrated knife at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your serrated knife back at you.')
                    printWithPause(0.5, '\033[31m', 'You are now bleeding.')
                    self.bleedingDamage = greater(self.bleedingDamage, 5)
                    self.turnsOfBleedingDamage = 10
                    self.inventory.remove('serrated knife')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
        if 'combustible lemon' in self.inventory:
            targetId = getInput('\033[96m', 'Enter the id number of the foe you want to throw your combustible '
                                            "lemon at or 'r' to target a random foe:")
            enemy = getTarget(enemies, targetId)

            try:
                if enemy.type == 'alien nun' and enemy.twirlingNunchucks:
                    printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} used their nunchucks to '
                                                    f'reflect your combustible lemon back at you.')
                    printWithPause(0.5, '\033[31m', 'You are now burning and poisoned.')
                    self.burningDamage = greater(self.burningDamage, 5)
                    self.turnsOfBurningDamage = 10
                    self.poisonDamage = greater(self.poisonDamage, 5)
                    self.turnsOfPoisonDamage = 10
                    self.inventory.remove('combustible lemon')
                    raise AttributeError

                if enemy.type in ['alien priest', 'sun priest', 'alien bishop'] and [foe for foe in enemies if
                                                                     foe.type in ['alien worshipper', 'alien cardinal']
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
        print('')
        printWithPause(0.5, '\033[96m', 'Your one time use items are:')

        for item in self.inventory:
            if item in oneTimeUseItems:
                printWithPause(0.5, '\033[00m', f'   {item}')

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
        if self.potions > 0:
            oldHp = self.hp
            self.heal(50)
            printWithPause(0.5, '\033[96m', f'You used a potion. You regained {self.hp - oldHp} '
                                            f'hit points.')
            self.potions -= 1

        else:
            printWithPause(0.5, '\033[96m', 'You do not have a potion.')

    def updateStats(self):
        self.standardAttack = 10 + self.inventory.count('sword') * 5
        self.maxHp = self.initialHp + self.inventory.count('armor') * 15
        self.attack = self.temporaryAttack + self.standardAttack

        if self.temporaryAttackDuration <= 0:
            self.temporaryAttack = 0

        else:
            self.temporaryAttackDuration -= 1

    def releaseSoul(self):
        try:
            soulId = getInput('\033[96m', "Type the id of the soul you want to release:")
            soul = [enemy for enemy in self.souls if enemy.number == int(soulId)][0]
            self.souls.remove(soul)
            self.newFoes.append(soul)
            printWithPause(0.5, '\033[96m', f"You released the soul of {soul.getPrintName()}.")

        except (ValueError, IndexError):
            pass

    def useSacrificialDagger(self):
        hpSacrificed = int(getInput('\033[96m', 'How much hp will you turn into extra temporary attack:'))

        if hpSacrificed > 0:
            printWithPause(0.5, '\033[31m', f'You got {hpSacrificed} extra temporary attack and '
                                            f'lost {hpSacrificed} hp.')
            self.temporaryAttackDuration = 3
            self.temporaryAttack = hpSacrificed
            self.hp -= hpSacrificed

    def getCustomInput(self):
        action = getInput('\033[96m', "What will you do? Type 'y' to exit the terminal for custom inputs:")

        if action == 'other':
            return 1

        elif action != 'y':
            try:
                exec(action)

            except Exception as error:
                printWithPause(0.5, '\033[31m', f'Your command raised an error saying, "{error}."')

            self.getCustomInput()

        return 0

    def actions(self, enemies, level):
        self.blocking = 0
        self.damageReduction = 0

        if not self.sunPriestSpotted and self.enemiesKilledInLevelFour >= 15:
            self.sunPriestSpotted = 1
            printWithPause(5, '\033[35m', "You have made a gap in the mob surrounding you. "
                                          "Through the gap, you see a cathedral in the distance.")

        if self.stun:
            self.stun = 0
            printWithPause(0.5, '\033[96m', 'You are stunned.')

        else:
            if 'sacrificial dagger' in self.inventory and self.temporaryAttackDuration <= 0 \
                    and getInput('\033[96m', "Will you use your sacrificial dagger? y/n:") == 'y':
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

            action = getInput('\033[96m', getListOfThingsWithCommas('or', actionList, ':'))

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

            elif action == 'other' and self.getCustomInput():
                return 'terminal'

            for i in range(self.inventory.count('knife')):
                if [enemy for enemy in enemies if enemy.hp > 0 and not enemy.possessed]:
                    self.knifeAttack(enemies)

            for i in range(self.inventory.count('butterfly knife')):
                if [enemy for enemy in enemies if enemy.hp > 0 and not enemy.possessed]:
                    self.butterflyKnifeAttack(enemies)

            if 'drone' in self.inventory:
                self.drone.actions(enemies, self)

    def getHurtByDebuffs(self):
        if self.poisonDamage:
            self.hp -= self.poisonDamage
            printWithPause(0.5, '\033[31m', f'You took {self.poisonDamage} damage from poison.')

            if self.turnsOfPoisonDamage <= 0:
                self.poisonDamage = 0

            self.turnsOfPoisonDamage -= 1

        if self.bleedingDamage:
            self.hp -= self.bleedingDamage
            printWithPause(0.5, '\033[31m', f'You took {self.bleedingDamage} damage from bleeding.')

            if self.turnsOfBleedingDamage <= 0:
                self.bleedingDamage = 0

            self.turnsOfBleedingDamage -= 1

        if self.burningDamage:
            self.hp -= self.burningDamage
            printWithPause(0.5, '\033[31m', f'You took {self.burningDamage} damage from bleeding.')

            if self.turnsOfBurningDamage <= 0:
                self.burningDamage = 0

            self.turnsOfBurningDamage -= 1

    def performNecessaryFunctions(self, enemies, level):
        self.showHp()
        self.getRegen()
        self.getHurtByDebuffs()
        whatToReturn = self.actions(enemies, level)

        if not [enemy for enemy in enemies if enemy.type == 'sun priest']:
            if level == 4:
                self.durationInLevelFour += 1

            if self.durationInLevelFour in [25, 37, 49, 61]:
                printWithPause(2, '\033[35m', "Aliens from further away than before are now aware of your "
                                              "presence and head off to attack you.")

        return whatToReturn

