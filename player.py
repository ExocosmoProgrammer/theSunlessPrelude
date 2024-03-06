import random

from definitions import (lesser, printWithPause, getReducedDamage, percentChance, getTarget,
                         getListOfThingsWithCommas, greater, getInput, getRandomItemsFromList)
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
        self.isDrone = 0
        self.poisonDamage = 0
        self.turnsOfPoisonDamage = 0
        self.bleedingDamage = 0
        self.turnsOfBleedingDamage = 0
        self.burningDamage = 0
        self.turnsOfBurningDamage = 0
        self.foesEncountered = []
        self.lockedBoxPuzzles = [self.playTicTacToeAgainstTheSunPriest, self.playMovementPuzzle]

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

    def basicAttack(self, enemies):
        """self.basicAttack(self, enemies) makes self perform  basic attack."""

        if 'sacrificial dagger' in self.inventory and self.attack == self.standardAttack and not \
                [enemy for enemy in enemies if enemy.type == 'helpless sun priest'] \
                and getInput('\033[96m', "Will you use your sacrificial dagger? y/n:") == 'y':
            self.useSacrificialDagger()
            self.updateStats()

        if enemies:
            targetId = getInput('\033[96m', "Enter the id number of the foe that you want to attack or "
                                            "'r' to attack a random foe:")

            enemy = getTarget(enemies, targetId)
            # If your input on who to attack is invalid, then targetId will be equal to none and the code in the next
            # try loop will raise Attribute Error.

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
                        damageInflicted = getReducedDamage(self.attack, enemy)
                        printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()}, inflicting '
                                                        f'{damageInflicted} '
                                                        f'damage.')

                    else:
                        damageInflicted = getReducedDamage(self.attack, enemy) * 2
                        printWithPause(0.5, '\033[93m', f'You hit {enemy.getPrintName()} with a critical '
                                                        f'attack, inflicting {damageInflicted} damage.')

                    enemy.hp -= damageInflicted
                    # enemy.twirlingNunchucks is 1 if the enemy is a nun or mother superior that is using its ability
                    # of twirling nunchucks else 0.

                    if enemy.twirlingNunchucks:
                        self.hp -= self.attack
                        printWithPause(0.5, '\033[91m', f'{enemy.getPrintName()} deflected your attack '
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

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You are in an empty room.')

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

        if self.temporaryAttackDuration <= 0:
            self.temporaryAttack = 0

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

        if not self.sunPriestSpotted and self.enemiesKilledInLevelFour >= 15:
            self.sunPriestSpotted = 1
            printWithPause(5, '\033[95m', "You have made a gap in the mob surrounding you. "
                                          "Through the gap, you see a cathedral in the distance.")

        if self.stun:
            self.stun = 0
            printWithPause(0.5, '\033[96m', 'You are stunned.')

        else:
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

                if 'drone' in self.inventory:
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
        for enemy in [enemy for enemy in bestiaryOrder if enemy in self.foesEncountered]:
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
            lines.append({f'{i}1': board[f'{i}1'], f'{i}2': board[f'{i}2'], f'{i}3': board[f'{i}3']})

        for i in range(1, 4):
            lines.append({f'a{i}': board[f'a{i}'], f'b{i}': board[f'b{i}'], f'c{i}': board[f'c{i}']})

        lines.append({'a1': board['a1'], 'b2': board['b2'], 'c3': board['c3']})
        lines.append({'c1': board['c1'], 'b2': board['b2'], 'a3': board['a3']})
        return lines

    def showTicTacToeBoard(self, board):
        print('\033[97m', '      1     2     3')
        print('\033[97m', '   ------------------')

        for i in ['a', 'b', 'c']:
            print('\033[97m', f'{i} |  {board[f"{i}1"]}  |  {board[f"{i}2"]}  |  '
                              f'{board[f"{i}3"]}  |')
            print('\033[97m', '   ------------------')

    def showMovementPuzzleBoard(self, board, visitedSpaces, requiredTiles):
        colorsForTiles = {'     ': '\033[00m', '  i  ': '\033[95m', ' ||| ': '\033[97m', '  !  ': '\033[91m',
                          '  o  ': '\033[93m'}
        print('\033[97m', '-------------------------------------------------------')

        for j in range(9):
            text = '|'

            for i in range(9):
                if board[(i, j)] == '     ':
                    hasFireball = False

                    for enemy in [enemy for enemy in board.values() if type(enemy) == movementPuzzleFoe]:
                        if [fireball for fireball in enemy.fireballs if fireball.coordinate == [i, j]]:
                            hasFireball = True
                            break

                    if hasFireball:
                        text += '\033[91m  *  \033[97m'

                    elif [i, j] in requiredTiles and [i, j] not in visitedSpaces:
                        text += '\033[93m  o  \033[97m|'

                    else:
                        text += '     \033[97m|'

                elif type(board[(i, j)]) == movementPuzzleFoe:
                    text += board[(i, j)].__str__() + '\033[97m|'

                else:
                    text += colorsForTiles[board[(i, j)]] + board[(i, j)] + '\033[97m|'

            print('\033[97m', text)
            print('\033[97m', '-------------------------------------------------------')

    def playTicTacToeAgainstTheSunPriest(self):
        board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(board)

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
                    emptySpace = [point for point in lineFinished.keys() if board[point] == ' '][0]

                elif almostFinishedXLines:
                    lineStopped = random.choice(almostFinishedXLines)
                    emptySpace = [point for point in lineStopped.keys() if board[point] == ' '][0]

                else:
                    emptySpace = random.choice([key for key in list(board.keys()) if board[key] == ' '])

                board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            lines = self.getLinesInTicTacToe(board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstTheAlienWarrior(self):
        board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')
                return 2

            lines = self.getLinesInTicTacToe(board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            try:
                emptySpace = random.choice([key for key in list(board.keys()) if board[key] == ' '])
                board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')

            lines = self.getLinesInTicTacToe(board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstTheAlienPilot(self):
        board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            try:
                almostFinishedOLines = [line for line in lines if \
                                        list(line.values()).count('O') == 2 and \
                                        list(line.values()).count(' ')]

                if almostFinishedOLines:
                    lineFinished = random.choice(almostFinishedOLines)
                    emptySpace = [point for point in lineFinished.keys() if board[point] == ' '][0]

                else:
                    emptySpace = random.choice([key for key in list(board.keys()) if board[key] == ' '])

                board[emptySpace] = 'O'

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            lines = self.getLinesInTicTacToe(board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstADrone(self):
        board = {}
        columnNumbers = {'a': 1, 'b': 2, 'c': 3}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                board[f'{i}{j}'] = ' '

        printWithPause(2, '\033[97m', 'You see the drone move aside to reveal...')
        printWithPause(2, '\033[91m', 'The alien commander!')
        printWithPause(2, '\033[97m', 'Taking advantage of your surprise, he takes the first turn.')
        turn = 1

        while True:
            try:
                if turn == 1:
                    emptySpace = random.choice(['a1', 'a3', 'c1', 'c3'])

                else:
                    enemySpots = [tile for tile in list(board.keys()) if board[tile] == 'O']
                    playerSpots = [tile for tile in list(board.keys()) if board[tile] == 'O']




                board[emptySpace] = 'O'
                turn += 1

            except IndexError:
                printWithPause(0.5, '\033[97m', 'you drew')
                return 2

            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will you take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you won')
                return 1

            lines = self.getLinesInTicTacToe(board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'you lost')
                return 0

    def playTicTacToeAgainstAPlayer(self):
        board = {}

        for i in ['a', 'b', 'c']:
            for j in range(1, 4):
                board[f'{i}{j}'] = ' '

        while True:
            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will player 1 take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'X'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(board)

            if ['X', 'X', 'X'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'player 1 won')
                return 1

            if not [list(board.values()).count(' ')]:
                printWithPause(0.5, '\033[97m', 'You drew.')

            self.showTicTacToeBoard(board)
            spaceTaken = getInput('\033[97m', 'Which available space will player 2 take? '
                                              'Type the name of the row of the space and then the number of the column '
                                              'of the space:')

            try:
                if board[spaceTaken] == ' ':
                    board[spaceTaken] = 'O'

                else:
                    printWithPause(0.5, '\033[97m', 'The space is taken.')

            except KeyError:
                printWithPause(0.5, '\033[97m', 'The space does not exist.')

            lines = self.getLinesInTicTacToe(board)

            if ['O', 'O', 'O'] in [list(line.values()) for line in lines]:
                printWithPause(0.5, '\033[97m', 'player 2 won')
                return 0

            if not [list(board.values()).count(' ')]:
                printWithPause(0.5, '\033[97m', 'You drew.')

    def playMovementPuzzle(self):
        board = {}
        playerSpace = [4, 8]
        visitedSpaces = [[4, 8]]
        directionsPerKey = {'w': [0, -1], 'a': [-1, 0], 's': [0, 1], 'd': [1, 0]}

        for i in range(9):
            for j in range(9):
                board[(i, j)] = '     '

        for i in range(5):
            for j in range(5):
                board[(2 * j + 1, 2 * i + 1)] = ' ||| '

        for i in range(5):
            for j in getRandomItemsFromList([h * 2 for h in range(5)], 2):
                board[(j, 2 * i + 1)] = ' ||| '

        for i in [0, 2, 4]:
            xCoord = random.randint(0, 8)
            board[(xCoord, i)] = movementPuzzleFoe([xCoord, i],
                                                   random.choice(['mage', 'charging', 'basic']), board)

        board[(4, 8)] = '  i  '
        requiredTiles = []

        for i in range(9):
            requiredTiles.append(random.choice([list(key) for key in board.keys() if board[key] == '     ' and \
                                                  key[1] == i]))

        print(requiredTiles)

        while True:
            self.showMovementPuzzleBoard(board, visitedSpaces, requiredTiles)

            for key in [key for key in board.keys() if type(board[key]) is movementPuzzleFoe]:
                enemy = board[key]
                board = enemy.action(board, playerSpace)

                for fireball in enemy.fireballs:
                    if fireball.move(board):
                        enemy.fireballs.remove(fireball)

            movement = getInput('\033[97m', 'Where will you go? Use wasd:')

            for i in range(200):
                print(' ')

            if movement in list(directionsPerKey.keys()):
                direction = directionsPerKey[movement]
                newLocation = (playerSpace[0] + direction[0], playerSpace[1] + direction[1])

                if newLocation in board.keys() and board[newLocation] != ' ||| ':
                    for i in [i for i in list(board.keys()) if board[i] == '  i  ']:
                        board[i] = '     '

                    playerSpace = list(newLocation)

                    if playerSpace not in visitedSpaces:
                        visitedSpaces.append(playerSpace)

            for key in [key for key in board.keys() if type(board[key]) is movementPuzzleFoe]:
                enemy = board[key]

                if enemy.coordinate == playerSpace or '  i  ' in enemy.tilesSkipped:
                    printWithPause(2, '\033[97m', 'You lost.')
                    return 0

                for fireball in enemy.fireballs:
                    if fireball.coordinate == playerSpace:
                        printWithPause(2, '\033[97m', 'You lost.')
                        return 0

            board[tuple(playerSpace)] = '  i  '

            if not [item for item in requiredTiles if not item in visitedSpaces]:
                printWithPause(2, '\033[97m', 'You won.')
                return 1

    def tryToOpenBox(self):
        if self.lockedBoxPuzzles and self.lockedBoxPuzzles[0]() == 1:
            self.lockedBoxPuzzles.pop(0)
            printWithPause(1, '\033[96m', 'A lock opened in your box.')

            if not self.lockedBoxPuzzles:
                printWithPause(2, '\033[96m', 'You opened your box.')
