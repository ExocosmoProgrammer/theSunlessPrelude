import random

from variables import bossesPerLevel
from definitions import printWithPause, getReducedDamage, greater, percentChance

hpPerFoe = {'alien colonist': 10, 'alien bodyguard': 20, 'alien police': 30,
            'alien soldier': 40, 'alien secret service': 50, 'alien commander': 200,
            'alien attacker': 10, 'alien protector': 50, 'drone': 10, 'idol': 30,
            'alien assassin': 10, 'alien minion': 30, 'alien general': 50,
            'alien scientist': 50, 'alien henchman': 75, 'alien pilot': 500,
            'alien combat scientist': 30, 'alien warrior': 750, 'alien doctor': 10,
            'alien priest': 30, 'alien worshipper': 1, 'alien gangster': 30,
            'alien cultist': 30, 'alien nun': 50, 'sun priest': 3000, 'alien bishop': 50,
            'alien cardinal': 1}
attackPerFoe = {'alien colonist': 2, 'alien bodyguard': 3, 'alien police': 6,
                'alien soldier': 7, 'alien secret service': 8, 'alien commander': 5,
                'alien attacker': 15, 'alien protector': 0, 'drone': 3, 'idol': 5,
                'alien assassin': 15, 'alien minion': 5, 'alien general': 4,
                'alien scientist': 6, 'alien henchman': 8, 'alien pilot': 10,
                'alien combat scientist': 6, 'alien warrior': 20, 'alien doctor': 5,
                'alien priest': 5, 'alien worshipper': 1, 'alien gangster': 10,
                'alien cultist': 7, 'alien nun': 5, 'sun priest': 5, 'alien bishop': 5,
                'alien cardinal': 5}
lootPerFoe = {'alien colonist': {'regen': 15}, 'alien bodyguard': {'shield': 15},
              'alien police': {'baton': 15}, 'alien soldier': {'knife': 15},
              'alien secret service': {'gun': 15}, 'alien assassin': {'stun grenade': 100},
              'alien minion': {'throwing knife': 100}, 'alien scientist': {'solution': 100},
              'alien general': {'sword': 50}, 'alien henchman': {'armor': 50},
              'alien combat scientist': {'solution': 100},
              'alien doctor': {'solution': 50, 'throwing knife': 50},
              'alien cultist': {'vial of poison': 100}, 'alien nun': {'nunchucks': 15},
              'alien priest': {'cross': 15}, 'alien gangster': {'butterfly knife': 15}}


class foe:
    def __init__(self, name, number, scanned=0, givesPotions=1, possessed=0, loot=None):
        self.type = name
        self.number = number
        self.scanned = scanned
        self.fullName = f'{name} {number}'
        self.hp = hpPerFoe[name]
        self.attack = attackPerFoe[name]
        self.gunWeakness = 1
        self.givesPotions = givesPotions
        self.bleedingDamage = 0
        self.poisonDamage = 0
        self.stun = 0
        self.foe = 1
        self.nunchuckDebuff = 0
        foeAttackMethods = {'alien commander': self.actAsAlienCommander,
                            'idol': self.actAsIdol,
                            'alien protector': self.actAsAlienProtector,
                            'alien scientist': self.actAsAlienScientist,
                            'alien general': self.actAsAlienGeneral,
                            'alien assassin': self.actAsAlienAssassin,
                            'alien doctor': self.actAsAlienDoctor,
                            'alien pilot': self.actAsAlienPilot,
                            'alien combat scientist': self.actAsAlienCombatScientist,
                            'alien warrior': self.actAsAlienWarrior,
                            'alien priest': self.actAsAlienPriest,
                            'sun priest': self.actAsSunPriest}
        self.damageReduction = 0
        self.newFoes = []
        self.timesSummoned = 0
        self.strengthened = 0
        self.preparingGrenade = 0
        self.possessed = possessed
        self.blocking = 0
        self.nextAttack = 'summon'
        self.cooldown = 3
        self.standardAttack = self.attack
        self.lastPtAttackMethodUsed = 1
        self.recentSummonQty = 0
        self.durationUntilRecentSummonQtyReset = 0

        try:
            self.attackMethod = foeAttackMethods[name]

        except KeyError:
            self.attackMethod = self.basicAttack

        try:
            self.loot = lootPerFoe[name]

        except KeyError:
            self.loot = {}

        if loot is not None:
            self.loot = loot

    def handleRecentSummonQty(self):
        self.durationUntilRecentSummonQtyReset -= 1

        if self.durationUntilRecentSummonQtyReset <= 0:
            self.durationUntilRecentSummonQtyReset = 5
            self.recentSummonQty = 0

    def basicAttack(self, target, number, enemies):
        if self.controlledByPro and [enemy for enemy in enemies if not enemy.possessed and
                                     enemy.hp > 0] and self.stun <= 0:
            targetId = input(f"Enter the id number of the foe you want {self.getPrintName()} to attack or "
                             "'r' to attack a random foe:")
            target = getTarget(enemies, targetId)

            try:
                if self.strengthened:
                    damageTaken = getReducedDamage(self.attack, target) * 2

                else:
                    damageTaken = getReducedDamage(self.attack, target)

                if target.type == 'alien commander' and [enemy for enemy in enemies if
                                                         enemy.type == 'alien protector']:
                    printWithPause(f'{self.getPrintName()} hit {target.getPrintName()}, but they were immune.')

                elif target.type in ['alien priest', 'sun priest'] and [enemy for enemy in enemies if
                                                                        enemy.type == 'alien worshipper' and
                                                                        enemy.hp > 0 and enemy.possessed ==
                                                                        target.possessed]:
                    attackedFoe = random.choice([enemy for enemy in enemies if
                                                 enemy.type == 'alien worshipper'
                                                 and enemy.hp > 0 and enemy.possessed ==
                                                 target.possessed])
                    attackedFoe.hp = 0
                    printWithPause(f"{attackedFoe.getPrintName()} got in the way of {self.getPrintName()}'s attack.")

                else:
                    printWithPause(f'{self.getPrintName()} attacked {target.getPrintName()}, '
                                   f'inflicting {damageTaken} damage.')
                    target.hp -= damageTaken

                self.gunWeakness = 0

            except AttributeError:
                pass

        elif self.stun <= 0:
            if self.strengthened:
                target.hp -= 5

                if self.possessed:
                    printWithPause(f'{self.getPrintName()} hit {target.getPrintName()}, '
                                   f'inflicting 5 damage.')

                else:
                    if target.foe:
                        printWithPause(f'{self.getPrintName()} hit {target.getPrintName()}, '
                                       f'inflicting 5 damage.')

                    elif not self.scaredOfCockroach:
                        printWithPause(f'You were hit by {self.getPrintName()}, inflicting '
                                       f'5 damage.')

                        if 'hissing cockroach' in target.inventory:
                            self.scaredOfCockroach = 1
                            printWithPause(f'Your cockroach hissed at {self.getPrintName()}, scaring them.')

            if random.randint(0, 1):
                damageTaken = None

                if target.foe or not self.scaredOfCockroach:
                    if self.strengthened:
                        damageTaken = getReducedDamage(self.attack, target) * 2

                    else:
                        damageTaken = getReducedDamage(self.attack, target)

                if target.foe:
                    if target.type in ['alien priest', 'sun priest'] and [enemy for enemy in enemies if
                                                                          enemy.type == 'alien worshipper']:
                        target = random.choice([enemy for enemy in enemies if
                                                enemy.type == 'alien worshipper'])
                        print(f"{target.getPrintName()} blocked {self.getPrintName()}'s attack.")

                    else:
                        printWithPause(f'{self.getPrintName()} attacked {target.getPrintName()}, '
                                       f'inflicting {damageTaken} damage.')

                elif not self.scaredOfCockroach:
                    if self.type == 'alien gangster':
                        if target.blocking:
                            damageTaken *= 4
                            printWithPause(f'{self.getPrintName()} shot you with their gun, '
                                           f'inflicting {damageTaken} damage. '
                                           f'You failed to block the shot.')

                        elif self.nunchuckDebuff:
                            damageTaken *= 2
                            printWithPause(f'{self.getPrintName()} shot you with their gun, '
                                           f'inflicting {damageTaken} damage. '
                                           f'You failed to hit the shot with your nunchucks.')

                        else:
                            printWithPause(f'{self.getPrintName()} attacked you, inflicting '
                                           f'{damageTaken} damage.')

                    elif target.blocking:
                        printWithPause(f'{self.getPrintName()} attacked you, inflicting '
                                       f'{damageTaken} damage, causing them to bleed.')
                        self.bleedingDamage = greater(self.bleedingDamage, 3)

                    else:
                        printWithPause(f'{self.getPrintName()} attacked you, inflicting '
                                       f'{damageTaken} damage.')

                        if self.nunchuckDebuff:
                            self.hp -= damageTaken * 4
                            printWithPause(f"{self.getPrintName()}'s attack hit your nunchucks, inflicting "
                                           f"{damageTaken * 4} damage to the foe.")

                    if 'hissing cockroach' in target.inventory:
                        printWithPause(f'Your cockroach hissed at {self.getPrintName()}, scaring them.')
                        self.scaredOfCockroach = 1

                if damageTaken is not None:
                    target.hp -= damageTaken
                    self.gunWeakness = 0

            elif not self.strengthened:
                self.gunWeakness = 1

        else:
            self.stun -= 1
            self.gunWeakness = 1
            printWithPause(f'{self.getPrintName()} is stunned.')

        self.nunchuckDebuff = 0

        if self.scaredOfCockroach > 0:
            self.scaredOfCockroach -= 0.5

    def getHurtByDebuffs(self, player):
        if self.stun and not self.poisonDamage and 'gas canister' in player.inventory:
            self.poisonDamage = 3
            printWithPause(f'{self.getPrintName()} is poisoned from your gas canister.')

        if self.bleedingDamage:
            self.hp -= self.bleedingDamage
            printWithPause(f'{self.getPrintName()} took {self.bleedingDamage} damage '
                           f'from bleeding.')

            if 'vial of diseased blood' in player.inventory:
                self.hp -= 3
                printWithPause(f'{self.getPrintName()} took 3 damage from the disease in their blood.')

        if self.poisonDamage:
            self.hp -= self.poisonDamage
            printWithPause(f'{self.getPrintName()} took {self.poisonDamage} damage '
                           f'from poison.')

        if self.controlledByPro:
            self.hp -= 5
            printWithPause(f'{self.getPrintName()} lost 5 hp.')

        if self.burnDamage:
            self.hp -= self.burnDamage
            printWithPause(f'{self.getPrintName()} took {self.burnDamage} from burning.')
        
    def actAsIdol(self, target, number, enemies):
        target.hp -= 5
        self.gunWeakness = 0

        if self.possessed:
            printWithPause(f"{target.getPrintName()} is hurt by an idol's presence, "
                           f"inflicting 5 damage.")

        else:
            printWithPause(f"You are hurt by an idol's presence, inflicting 5 damage.")

        if self.stun:
            printWithPause(f'{self.getPrintName()} cannot be stunned.')

    def actAsAlienProtector(self, target, number, enemies):
        printWithPause(f'{self.getPrintName()} is protecting the commander.')

    def empowerEnemyAsScientist(self, enemies):
        try:
            if self.possessed:
                foeWeakened = random.choice([enemy for enemy in enemies if
                                             not enemy.possessed])
                foeWeakened.standardAttack /= 2
                printWithPause(f'{self.getPrintName()} is weakening '
                               f'{foeWeakened.getPrintName()}.')

            else:
                foeStrengthened = random.choice([enemy for enemy in enemies if not
                                                 enemy.strengthened and not enemy.possessed])
                foeStrengthened.strengthened = 1
                printWithPause(f'{self.getPrintName()} is empowering '
                               f'{foeStrengthened.getPrintName()}.')

        except IndexError:
            if self.possessed:
                self.strengthened = 1
                printWithPause(f'{self.getPrintName()} is empowering '
                               f'{self.getPrintName()}.')
        
    def actAsAlienScientist(self, target, number, enemies):
        if not self.stun and percentChance(33):
            self.empowerEnemyAsScientist(enemies)

        self.basicAttack(target, number, enemies)

    def actAsAlienCombatScientist(self, target, number, enemies):
        if not self.stun:
            self.empowerEnemyAsScientist(enemies)

        self.basicAttack(target, number, enemies)

    def actAsAlienGeneral(self, target, number, enemies):
        otherFoes = [enemy for enemy in enemies if not enemy.possessed]

        if ((not self.possessed or len(otherFoes) > 1) and (not self.stun and percentChance(33)) and
                self.recentSummonQty < 4):
            self.newFoes.append(foe('drone', number, scanned=self.scanned,
                                    possessed=self.possessed))
            printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
            self.recentSummonQty += 1

        self.basicAttack(target, number, enemies)
        self.handleRecentSummonQty()

    def actAsAlienAssassin(self, target, number, enemies):
        if not self.stun:
            if not self.preparingGrenade and percentChance(50):
                self.preparingGrenade = 1
                printWithPause(f'{self.getPrintName()} is preparing a stun grenade.')

            elif self.preparingGrenade:
                if not self.possessed:
                    self.preparingGrenade = 0
                    target.stun = 1
                    printWithPause('You were hit by a stun grenade. You are now stunned.')

                else:
                    printWithPause(f'A stun grenade was thrown, stunning all enemies in '
                                   f'the room that you are in.')

                    for enemy in enemies:
                        enemy.stun = 2
                        printWithPause(f'{enemy.getPrintName()} was stunned for 2 turns '
                                       f'by the stun grenade.')

        self.basicAttack(target, number, enemies)

    def actAsAlienDoctor(self, target, number, enemies):
        if not self.stun:
            if percentChance(50):
                for enemy in enemies:
                    if enemy.type in ['alien warrior', 'sun priest']:
                        enemy.hp += 3
                        printWithPause(f'{self.getPrintName()} regenerated 3 hp of '
                                       f'{enemy.getPrintName()}.')
                        break

    def actAsAlienPriest(self, target, number, enemies):
        if not self.stun:
            if (percentChance(33) and len([enemy for enemy in enemies if
                                          enemy.type == 'alien worshipper']) <= 1 and
                    self.recentSummonQty < 3):
                self.newFoes.append(foe('alien worshipper', number, scanned=1))
                number += 1
                printWithPause(f'{self.getPrintName()} summoned '
                               f'{self.newFoes[-1].getPrintName()}.')
                self.recentSummonQty += 1

        self.basicAttack(target, number, enemies)
        self.handleRecentSummonQty()

    def actAsAlienCommander(self, target, number, enemies):
        if not self.stun:
            if self.recentSummonQty < 7:
                if self.hp <= 67 and percentChance(33):
                    self.newFoes.append(foe('alien attacker', number))
                    number += 1
                    printWithPause(f'{self.getPrintName()} summoned alien attacker {number - 1} '
                                   f'to attack you.')
                    self.recentSummonQty += 1

                if percentChance(33):
                    self.newFoes.append(foe('drone', number))
                    printWithPause(f'{self.getPrintName()} summoned drone {number} '
                                   f'to attack you.')
                    number += 1
                    self.recentSummonQty += 1

        if self.hp <= 133 and self.timesSummoned == 0:
            self.newFoes.append(foe('alien protector', number))
            number += 1
            printWithPause(f'{self.getPrintName()} summoned alien protector {number - 1} '
                           f'to protect the commander.')
            self.timesSummoned = 1

        if self.hp <= 67 and self.timesSummoned < 2:
            self.newFoes.append(foe('alien protector', number))
            number += 1
            self.newFoes.append(foe('idol', number))
            number += 1
            printWithPause(f'{self.getPrintName()} summoned alien protector {number - 2} '
                           f'to protect the commander.')
            printWithPause(f'{self.getPrintName()} summoned idol {number - 1} '
                           f'to attack you.')
            self.timesSummoned = 2

        if [enemy for enemy in enemies if enemy.type == 'alien protector']:
            printWithPause(f'{self.getPrintName()} is immune to damage.')

            if self.bleedingDamage:
                printWithPause(f"{self.getPrintName()}'s bleeding has stopped.")
                self.bleedingDamage = 0

        self.basicAttack(target, number, enemies)
        self.handleRecentSummonQty()


    def actAsAlienPilot(self, target, number, enemies):
        if not self.stun:
            if ((self.hp > 125 and percentChance(25)) or (self.hp <= 125 and percentChance(50))
                    and self.recentSummonQty < 2):
                foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                              'alien general', 'alien henchman']
                self.newFoes.append(foe(random.choice(foeChoices), number,
                                        scanned=self.scanned, givesPotions=0))
                printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                number += 1
                self.recentSummonQty += 1

            if ((self.hp <= 375 and self.timesSummoned == 0) or (self.hp <= 250
                                                                 and self.timesSummoned <= 1)):

                for i in range(3):
                    foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                                  'alien general', 'alien henchman']
                    self.newFoes.append(foe(random.choice(foeChoices), number,
                                            scanned=self.scanned, givesPotions=0))
                    printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.timesSummoned += 1

            elif self.hp <= 125 and self.timesSummoned <= 2:
                for i in range(3):
                    foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                                  'alien general', 'alien henchman']
                    self.newFoes.append(foe(random.choice(foeChoices), number,
                                            scanned=self.scanned, givesPotions=0))
                    printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.timesSummoned += 1

            for enemy in self.newFoes:
                if list(enemy.loot.keys())[0] in ['sword', 'armor']:
                    enemy.loot = {}

        self.basicAttack(target, number, enemies)
        self.handleRecentSummonQty()

    def actAsAlienWarrior(self, target, number, enemies):
        if not self.stun:
            self.cooldown -= 1

            if self.cooldown == 1:
                self.cooldown = 0

                if self.nextAttack == 'summon':
                    printWithPause(f'{self.getPrintName()} is preparing to summon foes.')

                elif self.nextAttack == 'explosion':
                    printWithPause(f'{self.getPrintName()} is preparing a grenade.')

                elif self.nextAttack == 'regen':
                    printWithPause(f'{self.getPrintName()} is preparing to summon doctors.')

            elif self.cooldown < 1:
                self.cooldown = 3

                if self.nextAttack == 'summon':
                    for i in range(2):
                        nextFoe = random.choice(['alien assassin', 'idol', 'alien soldier',
                                                 'alien combat scientist'])
                        self.newFoes.append(foe(nextFoe, number, scanned=self.scanned))
                        printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                        number += 1

                    self.nextAttack = 'regen'

                elif self.nextAttack == 'regen':
                    for i in range(3):
                        self.newFoes.append(foe('alien doctor', number, scanned=self.scanned))
                        printWithPause(f'{self.getPrintName()} summoned '
                                       f'{self.newFoes[-1].getPrintName()}.')
                        number += 1
                        self.nextAttack = 'explosion'

                elif self.nextAttack == 'explosion':
                    damageToPro = getReducedDamage(40, target)
                    target.hp -= damageToPro
                    printWithPause(f'You were hit by an explosion, inflicting {damageToPro} damage.')

                    for enemy in enemies:
                        enemy.hp -= 40
                        printWithPause(f'{enemy.getPrintName()} was hit by an explosion, '
                                       f'inflicting 40 damage.')

                    self.nextAttack = 'summon'

        self.basicAttack(target, number, enemies)

    def actAsSunPriestPt1(self, target, number, enemies):
        if not self.stun:
            if self.recentSummonQty < 1:
                if percentChance(25):
                    self.newFoes.append(foe(random.choice(['alien gangster', 'alien cultist']),
                                            number, scanned=1))
                    printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.newFoes.append(foe(random.choice(['alien nun', 'alien priest']),
                                            number, scanned=1))
                    printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.recentSummonQty += 1

            if self.hp <= 2900 and self.timesSummoned == 0:
                self.newFoes.append(foe('alien gangster', number, scanned=1))
                printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                number += 1
                self.timesSummoned = 1

            elif self.hp <= 2800 and self.timesSummoned <= 1:
                self.newFoes.append(foe('alien nun', number, scanned=1))
                printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                number += 1
                self.newFoes.append(foe('alien gangster', number, scanned=1))
                printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                number += 1
                self.timesSummoned = 2

        self.basicAttack(target, number, enemies)
        self.handleRecentSummonQty()

    def actAsSunPriestPt2(self, target, number, enemies):
        if self.lastPtAttackMethodUsed == 1:
            self.lastPtAttackMethodUsed = 2
            self.timesSummoned = 0
            printWithPause('The sun priest is changing its strategy.', 5)

        if not self.stun:
            self.cooldown -= 1

            if self.cooldown == 1:
                self.cooldown = 0

                if self.nextAttack == 'summon':
                    printWithPause(f'{self.getPrintName()} is preparing to summon foes.')

                elif self.nextAttack == 'explosion':
                    printWithPause(f'{self.getPrintName()} is preparing a grenade.')

                elif self.nextAttack == 'regen':
                    printWithPause(f'{self.getPrintName()} is preparing to summon doctors.')

            elif self.cooldown < 1:

                if self.nextAttack == 'summon':
                    foeChoices = (['alien gangster'] * 4 + ['alien cultist'] * 2 +
                                  ['alien worshipper'] * 3 + ['alien combat scientist'])

                    for i in range(3):
                        nextFoe = random.choice(foeChoices)
                        foeChoices.remove(nextFoe)
                        self.newFoes.append(foe(nextFoe, number, scanned=1))
                        printWithPause(f'{self.getPrintName()} summoned {self.newFoes[-1].getPrintName()}.')
                        number += 1

                    self.nextAttack = 'regen'
                    self.cooldown = 5

                elif self.nextAttack == 'regen':
                    for i in range(5):
                        self.newFoes.append(foe('alien doctor', number,
                                                scanned=1))
                        printWithPause(f'{self.getPrintName()} summoned '
                                       f'{self.newFoes[-1].getPrintName()}.')
                        number += 1

                    self.newFoes.append(foe('alien cultist', number,
                                            scanned=1))
                    printWithPause(f'{self.getPrintName()} summoned '
                                   f'{self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.newFoes.append(foe(random.choice(['alien gangster', 'alien cultist']),
                                            number, scanned=1))
                    number += 1
                    printWithPause(f'{self.getPrintName()} summoned '
                                   f'{self.newFoes[-1].getPrintName()}.')

                    self.nextAttack = 'explosion'
                    self.cooldown = 5

                elif self.nextAttack == 'explosion':
                    damageToPro = getReducedDamage(40, target)
                    target.hp -= damageToPro
                    printWithPause(f'You were hit by an explosion, inflicting {damageToPro} damage.')

                    for enemy in enemies:
                        enemy.hp -= 40
                        printWithPause(f'{enemy.getPrintName()} was hit by an explosion, '
                                       f'inflicting 40 damage.')

                    self.nextAttack = 'summon'
                    self.cooldown = 2

            self.basicAttack(target, number, enemies)

    def actAsSunPriest(self, target, number, enemies):
        if self.hp > 2700:
            self.actAsSunPriestPt2(target, number, enemies)

        else:
            self.actAsSunPriestPt2(target, number, enemies)

    def getDamage(self, enemies):
        if self.type == 'alien cultist':
            self.attack = self.standardAttack * len([enemy for enemy in enemies if
                                                     enemy.type == 'alien cultist'])

        else:
            self.attack = self.standardAttack

        if self.nunchuckDebuff:
            self.attack /= 2

    def handleStunImmunity(self):
        if self.type in list(bossesPerLevel.values()) and self.stun:
            self.stun = 0
            print(f'{self.getPrintName()} is immune to stun.')

    def getPrintName(self):
        return self.fullName if self.scanned else '???'

    def actAsFoe(self, target, number, enemies):
        self.getDamage(enemies)

        if self.hp > 0:
            self.attackMethod(target, number, enemies)

        self.getHurtByDebuffs()
