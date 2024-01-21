import random

from definitions import (getTarget, printWithPause, getReducedDamage, lesser, greater,
                         getListOfThingsWithCommas, getInput)


class drone:
    def __init__(self):
        self.inventory = []
        self.attack = 5
        self.temporaryAttack = 0
        self.temporaryAttackDuration = 0
        self.hp = 100
        self.foe = 0
        self.damageReduction = 0
        self.isDrone = 1

    def basicAttack(self, enemies, protagonist):
        """Gets input on the id number of whom to attack and attacks the enemy with the entered id number if possible,
        except if 'r' is typed in, in which case a random enemy will be attacked in the player's room if possible"""

        if enemies:
            targetId = getInput('\033[96m', "Enter the id number of the foe you want your drone to attack or "
                                            "'r' to attack a random foe:")

            enemy = getTarget(enemies, targetId)

            try:
                # If the foe your drone attacks is an alien priest or a sun priest and there worshippers on the
                # priest's side, a worshipper will get in the way of your attack.

                if (enemy.type in ['alien priest', 'sun priest'] and
                        [foe for foe in enemies if
                         foe.type == 'alien worshipper'
                         and foe.hp > 0 and foe.possessed ==
                         enemy.possessed]):
                    attackedFoe = random.choice([foe for foe in enemies if
                                                 foe.type == 'alien worshipper'
                                                 and foe.hp > 0 and foe.possessed ==
                                                 enemy.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f'{attackedFoe.getPrintName()} got in the way of '
                                                    f'your drone\'s attack.')

                # If the foe your drone hits is an alien commander, and there is an alien protector alive, the
                # commander will be immune to your drone's attack.

                elif enemy.type == 'alien commander' and [foe for foe in enemies if
                                                          foe.type == 'alien protector']:
                    printWithPause(0.5, '\033[93m', f'Your drone hit {enemy.getPrintName()}, but they were '
                                                    f'immune.')

                else:
                    damageInflicted = getReducedDamage(protagonist.attack / 2, enemy)
                    printWithPause(0.5, '\033[93m', f'Your drone hit {enemy.getPrintName()}, inflicting '
                                                    f'{damageInflicted} '
                                                    f'damage.')

                    enemy.hp -= damageInflicted

            # If getTarget cannot get a target in your drone's basicAttack function call, then getTarget will
            # return None, causing an AttributeError since an attempt will be made to access attributes of None.

            except AttributeError:
                pass

        else:
            printWithPause(0.5, '\033[96m', 'You are in an empty room.')

    def scan(self, enemies, protagonist):
        """Shows what enemies are in the player's room and makes future mentions of said enemies show their names"""
        print('')
        printWithPause(0.5, '\033[96m', 'The enemies in your room are:')
        # If you have a radio, then your drone's scans will always show the full names of all enemies that are in
        # your room.

        if 'radio' in protagonist.inventory:
            for enemy in enemies:
                enemy.scanned = 1
                printWithPause(0.5, '\033[96m', f'   {enemy.fullName}')

        # If you don't have a radio, then your drone's scans will show the full names of enemies that have been
        # scanned and '???' for enemies that have not been scanned.

        else:
            for enemy in enemies:
                printWithPause(0.5, '\033[96m', f'   {enemy.getPrintName()}')
                enemy.scanned = 1

        print('')

    def updateStats(self, protagonist):
        """Updates some stats of the drone"""
        self.hp = greater(self.hp, 0)
        self.attack = self.temporaryAttack + protagonist.attack / 2

        if self.temporaryAttackDuration <= 0:
            self.temporaryAttack = 0

        else:
            self.temporaryAttackDuration -= 1

    def giveItemToPro(self, protagnoist):
        """Gets input on what item to give to the player and tries to add said item to the player's inventory and
        remove said item from the player's inventory"""
        print('')
        print('Your drone\'s items are:')

        for thing in self.inventory:
            print(f'    {thing}')

        print('')
        item = getInput('\033[96m', 'What item will you get from your drone:')

        if protagnoist.inventory.count(item) < 2:
            try:
                self.inventory.remove(item)
                protagnoist.inventory.append(item)
                print(f'Your drone gave you {item}.')

            except ValueError:
                print(f'Your drone does not have {item}.')

        else:
            print(f'You cannot hold another {item}. Your drone keeps the {item}.')

    def useSacrificialDagger(self, protagonist):
        """Gets input on how much hp to sacrifice from the player. Whatever amount of hp is sacrificed from
        the player will be temporarily added to the drone's attack."""

        try:
            hpSacrificed = int(getInput('\033[96m', 'How much of your hp will your drone turn '
                                                    'into extra temporary attack:'))

            if hpSacrificed > 0:
                printWithPause(0.5, '\033[31m', f'Your drone got {hpSacrificed} extra temporary attack and '
                                                f'you lost {hpSacrificed} hp.')
                self.temporaryAttackDuration = 3
                self.temporaryAttack = hpSacrificed
                protagonist.hp -= hpSacrificed

        except ValueError:
            print('Invalid input')

    def actions(self, enemies, protagonist):
        """Handles the drone's turn"""
        self.hp = greater(self.hp, 0)
        self.showHp(protagonist)

        if 'sacrificial dagger' in self.inventory and self.temporaryAttackDuration <= 0 < self.hp \
                and getInput('\033[96m', "Will you use your sacrificial dagger? y/n:") == 'y':
            self.useSacrificialDagger(protagonist)

        self.updateStats(protagonist)
        actionList = ["Press 'h' to make your drone use a potion"]

        if self.hp:
            actionList += ["'a' to make your drone perform a basic attack",
                           "'s' to make your drone scan"]

            if self.inventory:
                actionList.append("'t' to get an item from your drone")

        action = getInput('\033[96m', getListOfThingsWithCommas('or', actionList, ending=':'))

        if action == 'h':
            self.heal(protagonist)

        elif action == 't' and self.inventory:
            self.giveItemToPro(protagonist)

        elif self.hp:
            if action == 'a':
                self.basicAttack(enemies, protagonist)

            elif action == 's':
                self.scan(enemies, protagonist)

    def heal(self, protagonist):
        """Uses one of the player's potions to heal the drone if the player has potions. The drone will heal by 50 hp
        or however much hp the drone must heal by to have 100 hp, whichever is lesser."""

        if protagonist.potions:
            hp = self.hp
            self.hp = lesser(self.hp + 50, 100)
            printWithPause(0.5, '\033[96m', f'Your drone used a potion, restoring {self.hp - hp} hit '
                                            f'points to your drone.')
            protagonist.potions -= 1

        else:
            print(f'You do not have a potion.')

    def showHp(self, protagonist):
        """Shows the drone's hp. Shows the drone's inventory as needed."""
        hpDashCount = int(self.hp / 10)
        emptySpaceCount = int(10 - hpDashCount)
        printWithPause(0.5, '\033[96m', f'Your drone has {self.hp} hit points, and you '
                       f'have {protagonist.potions} potions.')
        printWithPause(0.5, '\033[37m', '[', '\033[34m', f'{"_" * hpDashCount}{" " * emptySpaceCount}',
                       '\033[37m', ']')

        if self.inventory:
            print(f'Drone inventory: {self.inventory}')
