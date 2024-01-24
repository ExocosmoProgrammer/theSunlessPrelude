import random

from variables import bossesPerLevel, oneTimeUseItems
from definitions import printWithPause, getReducedDamage, greater, percentChance, getTarget, getInput

hpPerFoe = {'alien colonist': 10, 'alien bodyguard': 20, 'alien police': 30,
            'alien soldier': 40, 'alien secret service': 50, 'alien commander': 200,
            'alien attacker': 10, 'alien protector': 50, 'drone': 10, 'idol': 30,
            'alien assassin': 10, 'alien minion': 30, 'alien general': 50,
            'alien scientist': 50, 'alien henchman': 75, 'alien pilot': 500,
            'alien combat scientist': 30, 'alien warrior': 750, 'alien doctor': 10,
            'alien priest': 30, 'alien worshipper': 1, 'alien gangster': 30,
            'alien cultist': 30, 'alien nun': 50, 'sun priest': 3000, 'alien bishop': 50,
            'alien cardinal': 1, 'alien admiral': 50, 'stronger drone': 10, 'alien biologist': 50,
            'alien hitman': 20}
attackPerFoe = {'alien colonist': 2, 'alien bodyguard': 3, 'alien police': 6,
                'alien soldier': 7, 'alien secret service': 8, 'alien commander': 5,
                'alien attacker': 15, 'alien protector': 0, 'drone': 3, 'idol': 5,
                'alien assassin': 15, 'alien minion': 5, 'alien general': 4,
                'alien scientist': 6, 'alien henchman': 8, 'alien pilot': 10,
                'alien combat scientist': 6, 'alien warrior': 20, 'alien doctor': 5,
                'alien priest': 5, 'alien worshipper': 1, 'alien gangster': 10,
                'alien cultist': 7, 'alien nun': 5, 'sun priest': 10, 'alien bishop': 5,
                'alien cardinal': 10, 'alien admiral': 4, 'stronger drone': 2, 'alien biologist': 6,
                'alien hitman': 15}
lootPerFoe = {'alien colonist': {'regen': 15}, 'alien bodyguard': {'shield': 15},
              'alien police': {'baton': 15}, 'alien soldier': {'knife': 15},
              'alien secret service': {'gun': 15}, 'alien assassin': {'stun grenade': 100,
                                                                      'gas canister': 15},
              'alien minion': {'throwing knife': 100, 'radio': 10},
              'alien scientist': {'solution': 100, 'combustible lemon': 1, 'hissing cockroach': 15},
              'alien general': {'sword': 50, 'drone': 15},
              'alien henchman': {'armor': 50, 'serrated knife': 100, 'vial of diseased blood': 15},
              'alien combat scientist': {'solution': 100, 'combustible lemon': 1, 'hissing cockroach': 15},
              'alien doctor': {'solution': 50, 'throwing knife': 50},
              'alien cultist': {'vial of poison': 100}, 'alien nun': {'nunchucks': 15},
              'alien priest': {'cross': 15}, 'alien gangster': {'butterfly knife': 15},
              'alien biologist': {'solution': 50}}
poisonAttackPerFoe = {'alien biologist': 5}
enemiesWithoutGunWeakness = ['idol', 'stronger drone']


class foe:
    def __init__(self, name, number, scanned=0, givesPotions=1, possessed=0, loot=None,
                 controlledByPro=0, isSummon=0, **extraStats):
        self.type = name
        self.number = number
        self.scanned = scanned
        self.fullName = f'{name} {number}'
        self.hp = hpPerFoe[name]
        self.initialHp = self.hp
        self.attack = attackPerFoe[name]
        self.gunWeakness = 0 if name in enemiesWithoutGunWeakness else 1
        self.givesPotions = givesPotions
        self.bleedingDamage = 0
        self.poisonDamage = 0
        self.stun = 0
        self.foe = 1
        self.nunchuckDebuff = 0
        self.scaredOfCockroach = 0
        self.burnDamage = 0
        self.twirlingNunchucks = 0
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
                            'alien bishop': self.actAsAlienBishop,
                            'sun priest': self.actAsSunPriest,
                            'stronger drone': self.actAsStrongerDrone,
                            'alien admiral': self.actAsAlienAdmiral,
                            'alien biologist': self.actAsAlienCombatScientist,
                            'alien hitman': self.actAsAlienAssassin,
                            'alien nun': self.actAsAlienNun}
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
        self.controlledByPro = controlledByPro
        self.hitsUntilStunnedByBaton = 1
        self.turnsOfBleedingFromGun = 0
        self.bleedingDamageFromGun = 0
        self.isDrone = 0

        try:
            self.poisonAttack = poisonAttackPerFoe[self.type]

        except KeyError:
            self.poisonAttack = 0

        try:
            self.attackMethod = foeAttackMethods[name]

        except KeyError:
            self.attackMethod = self.basicAttack

        try:
            self.loot = lootPerFoe[name]

        except KeyError:
            self.loot = {}

        if isSummon:
            oldLoot = self.loot
            self.loot = {}

            for key in list(oldLoot.keys()):
                if key in oneTimeUseItems:
                    self.loot[key] = oldLoot[key] / 2

        if loot is not None:
            self.loot = loot

        for attribute in list(extraStats.keys()):
            exec(f'self.{attribute} = extraStats[attribute]')

    def handleRecentSummonQty(self):
        self.durationUntilRecentSummonQtyReset -= 1

        if self.durationUntilRecentSummonQtyReset <= 0:
            self.durationUntilRecentSummonQtyReset = 5
            self.recentSummonQty = 0

    def basicAttack(self, target, number, enemies, player):
        if self.controlledByPro and [enemy for enemy in enemies if not enemy.possessed and
                                                                   enemy.hp > 0] and self.stun <= 0:
            targetId = getInput('\033[96m',
                                f"Enter the id number of the foe you want {self.getPrintName()} to attack or "
                                "'r' to make them attack a random foe:")
            target = getTarget(enemies, targetId)

            try:
                if self.strengthened:
                    damageTaken = getReducedDamage(self.attack, target) * 2

                else:
                    damageTaken = getReducedDamage(self.attack, target)

                if target.type == 'alien commander' and [enemy for enemy in enemies if
                                                         enemy.type == 'alien protector']:
                    printWithPause(0.5, '\033[93m', f'{self.getPrintName()} hit '
                                                    f'{target.getPrintName()}, but they were immune.')

                elif target.type in ['alien priest', 'sun priest'] and [enemy for enemy in enemies if
                                                                        enemy.type in ['alien worshipper',
                                                                                       'alien cardinal'] and
                                                                        enemy.hp > 0 and enemy.possessed ==
                                                                        target.possessed]:
                    attackedFoe = random.choice([enemy for enemy in enemies if
                                                 enemy.type in ['alien worshipper', 'alien cardinal']
                                                 and enemy.hp > 0 and enemy.possessed ==
                                                 target.possessed])
                    attackedFoe.hp = 0
                    printWithPause(0.5, '\033[93m', f"{attackedFoe.getPrintName()} got in the way of "
                                                    f"{self.getPrintName()}'s attack.")

                else:
                    printWithPause(0.5, '\033[93m', f'{self.getPrintName()} attacked '
                                                    f'{target.getPrintName()}, inflicting {damageTaken} damage.')
                    target.hp -= damageTaken

                    if self.poisonAttack:
                        target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                        printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                        f'{target.getPrintName()}')
                        target.turnsOfPoisonDamage = 10

                    if target.twirlingNunchucks:
                        self.hp -= damageTaken
                        printWithPause(0.5, '\033[93m', f'{target.fullName} deflected {self.fullName}\'s '
                                                        f'attack, inflicting {damageTaken} damage to {self.fullName}.')

                self.gunWeakness = 0

            except AttributeError:
                pass

        elif self.stun <= 0:
            if self.strengthened:
                target.hp -= 5

                if self.possessed:
                    printWithPause(0.5, '\033[93m', f'{self.getPrintName()} hit {target.getPrintName()}, '
                                                    f'inflicting 5 damage.')

                    if self.poisonAttack:
                        target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                        printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                        f'{target.getPrintName()}')
                        target.turnsOfPoisonDamage = 10

                elif target.foe:
                    printWithPause(0.5, '\033[93m', f'{self.getPrintName()} hit '
                                                    f'{target.getPrintName()}, inflicting 5 damage.')

                    if self.poisonAttack:
                        target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                        printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                        f'{target.getPrintName()}')
                        target.turnsOfPoisonDamage = 10

                elif not self.scaredOfCockroach:
                    if target.isDrone:
                        printWithPause(0.5, '\033[31m', f'Your drone was hit by '
                                                        f'{self.getPrintName()}, inflicting 5 damage.')

                        if self.poisonAttack:
                            target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                            f'your drone.')
                            target.turnsOfPoisonDamage = 10

                    else:
                        printWithPause(0.5, '\033[31m', f'You were hit by {self.getPrintName()}, '
                                                        f'inflicting 5 damage.')

                        if self.poisonAttack:
                            target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                            f'you.')
                            target.turnsOfPoisonDamage = 10

                    if 'hissing cockroach' in target.inventory:
                        self.scaredOfCockroach = 1
                        printWithPause(0.5, '\033[96m', f'Your cockroach hissed at '
                                                        f'{self.getPrintName()}, scaring them.')

            if random.randint(0, 1):
                damageTaken = None

                if target.foe or not self.scaredOfCockroach:
                    if self.strengthened:
                        damageTaken = getReducedDamage(self.attack, target) * 2

                    else:
                        damageTaken = getReducedDamage(self.attack, target)

                if target.foe:
                    if target.type in ['alien priest', 'sun priest'] and [enemy for enemy in enemies if
                                                                          enemy.type in ['alien worshipper',
                                                                                         'alien cardinal']]:
                        target = random.choice([enemy for enemy in enemies if
                                                enemy.type in ['alien worshipper', 'alien cardinal']])
                        printWithPause(0.5, '\033[93m', f"{target.getPrintName()} blocked "
                                                        f"{self.getPrintName()}'s attack.")

                    else:
                        printWithPause(0.5, '\033[93m', f'{self.getPrintName()} attacked '
                                                        f'{target.getPrintName()}, inflicting {damageTaken} damage.')

                        if target.twirlingNunchucks:
                            self.hp -= damageTaken
                            printWithPause(0.5, '\033[93m', f'{target.fullName} reflected '
                                                            f'{self.getPrintName()}\'s attack, inflicting '
                                                            f'{damageTaken} damage to {self.fullName}.')

                elif not self.scaredOfCockroach:
                    if self.type == 'alien gangster':
                        if not target.isDrone and target.blocking:
                            damageTaken *= 4
                            printWithPause(0.5, '\033[31m', f'{self.getPrintName()} shot you with '
                                                            f'their gun, inflicting {damageTaken} damage. '
                                                            f'You failed to block the shot.')

                        elif self.nunchuckDebuff:
                            if target.isDrone:
                                printWithPause(0.5, '\033[31m', f'{self.getPrintName()} hit your drone, '
                                                                f'inflicting {damageTaken} damage.')

                            else:
                                damageTaken *= 2
                                printWithPause(0.5, '\033[31m', f'{self.getPrintName()} shot you '
                                                                f'with their gun, inflicting {damageTaken} damage. '
                                                                f'You failed to hit the shot with your nunchucks.')

                        elif target.isDrone:
                            printWithPause(0.5, '\033[31m', f'{self.getPrintName()} attacked your '
                                                            f'drone, inflicting {damageTaken} damage.')

                        else:
                            printWithPause(0.5, '\033[31m', f'{self.getPrintName()} attacked you, '
                                                            f'inflicting {damageTaken} damage.')

                    elif not target.isDrone and target.blocking:
                        printWithPause(0.5, '\033[31m', f'{self.getPrintName()} attacked you, inflicting '
                                                        f'{damageTaken} damage, causing them to bleed.')
                        self.bleedingDamage = greater(self.bleedingDamage, 3)

                    elif not target.isDrone:
                        printWithPause(0.5, '\033[31m', f'{self.getPrintName()} attacked you, inflicting '
                                                        f'{damageTaken} damage.')

                        if self.nunchuckDebuff:
                            self.hp -= damageTaken * 4
                            printWithPause(0.5, '\033[93m', f"{self.getPrintName()}'s attack was "
                                                            f"deflected by your nunchucks, inflicting "
                                                            f"{damageTaken * 4} damage to the foe.")

                            if self.twirlingNunchucks:
                                target.hp -= damageTaken
                                printWithPause(0.5, '\033[31m', f"{self.fullName} deflected your "
                                                                f"deflection, inflicting {damageTaken} damage to you.")

                    else:
                        printWithPause(0.5, '\033[31m', f'{self.getPrintName()} attacked your drone, '
                                                        f'inflicting {damageTaken} damage.')

                    if 'hissing cockroach' in player.inventory:
                        printWithPause(0.5, '\033[96m', f'Your cockroach hissed at '
                                                        f'{self.getPrintName()}, scaring them.')
                        self.scaredOfCockroach = 1

                if damageTaken is not None:
                    target.hp -= damageTaken
                    self.gunWeakness = 0

                    if self.poisonAttack:
                        target.poisonDamage = greater(self.poisonAttack, target.poisonDamage)
                        target.turnsOfPoisonDamage = 10

                        if target.foe:
                            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} poisoned '
                                                            f'{target.getPrintName()}.')

                        elif target.isDrone:
                            printWithPause(0.5, '\033[31m', f'{self.getPrintName()} poisoned your '
                                                            f'drone.')

                        else:
                            printWithPause(0.5, '\033[31m', f'{self.getPrintName()} poisoned you.')

            elif not self.strengthened:
                self.gunWeakness = 1

        else:
            self.stun -= 1
            self.gunWeakness = 1
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is stunned.')

        self.nunchuckDebuff = 0

        if self.scaredOfCockroach > 0:
            self.scaredOfCockroach -= 0.5

    def getHurtByDebuffs(self, protagonist):
        if self.stun and not self.poisonDamage and 'gas canister' in protagonist.inventory:
            self.poisonDamage = 3
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is poisoned from your gas canister.')

        if self.bleedingDamage:
            self.hp -= self.bleedingDamage
            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took {self.bleedingDamage} damage '
                                            f'from bleeding.')

            if 'vial of diseased blood' in protagonist.inventory:
                self.hp -= 3
                printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took 3 damage from the '
                                                f'disease in their blood.')

        if self.bleedingDamageFromGun:
            self.hp -= self.bleedingDamageFromGun
            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took {self.bleedingDamageFromGun} '
                                            f'damage from bleeding from their gunshot wound.')

            if 'vial of diseased blood' in protagonist.inventory and not self.bleedingDamage:
                self.hp -= 3
                printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took 3 damage from the '
                                                f'disease in their blood.')

            self.turnsOfBleedingFromGun -= 1

            if self.turnsOfBleedingFromGun <= 0:
                self.bleedingDamageFromGun = 0

        if self.poisonDamage:
            self.hp -= self.poisonDamage
            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took {self.poisonDamage} damage '
                                            f'from poison.')

        if self.burnDamage:
            self.hp -= self.burnDamage
            printWithPause(0.5, '\033[93m', f'{self.getPrintName()} took {self.burnDamage} from burning.')

    def actAsIdol(self, target, number, enemies, player):
        target.hp -= 5
        self.gunWeakness = 0

        if self.possessed:
            printWithPause(0.5, '\033[93m', f"{target.getPrintName()} is hurt by an idol's presence, "
                                            f"inflicting 5 damage.")

        else:
            printWithPause(0.5, '\033[31m', f"You are hurt by an idol's presence, inflicting 5 damage.")

        if self.stun:
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} cannot be stunned.')

    def actAsAlienProtector(self, target, number, enemies, player):
        printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is protecting the commander.')

    def empowerEnemyAsScientist(self, enemies):
        try:
            if self.possessed:
                foeWeakened = random.choice([enemy for enemy in enemies if
                                             not enemy.possessed])
                foeWeakened.standardAttack /= 2
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is weakening '
                                                f'{foeWeakened.getPrintName()}.')

            else:
                foeStrengthened = random.choice([enemy for enemy in enemies if not
                enemy.strengthened and not enemy.possessed])
                foeStrengthened.strengthened = 1
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is empowering '
                                                f'{foeStrengthened.getPrintName()}.')

        except IndexError:
            if self.possessed:
                self.strengthened = 1
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is empowering '
                                                f'{self.getPrintName()}.')

    def actAsAlienScientist(self, target, number, enemies, player):
        if not self.stun and percentChance(33):
            self.empowerEnemyAsScientist(enemies)

        self.basicAttack(target, number, enemies, player)

    def actAsAlienCombatScientist(self, target, number, enemies, player):
        if not self.stun:
            self.empowerEnemyAsScientist(enemies)

        self.basicAttack(target, number, enemies, player)

    def actAsAlienGeneral(self, target, number, enemies, player):
        otherFoes = [enemy for enemy in enemies if not enemy.possessed]

        if ((not self.possessed or len(otherFoes) > 1) and (not self.stun and percentChance(33)) and
                self.recentSummonQty < 4):
            self.newFoes.append(foe('drone', number, scanned=self.scanned,
                                    possessed=self.possessed, givesPotions=0))
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                            f'{self.newFoes[-1].getPrintName()}.')
            self.recentSummonQty += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsAlienAssassin(self, target, number, enemies, player):
        if not self.stun:
            if not self.preparingGrenade and percentChance(50):
                self.preparingGrenade = 1
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is preparing a stun grenade.')

            elif self.preparingGrenade:
                if not self.possessed:
                    self.preparingGrenade = 0
                    player.stun = 1
                    printWithPause(0.5, '\033[96m', 'You were hit by a stun grenade. You are now '
                                                    'stunned.')

                else:
                    printWithPause(0.5, '\033[96m', f'A stun grenade was thrown, stunning enemies in '
                                                    f'the room that you are in.')

                    for enemy in enemies:
                        if not enemy.possessed:
                            enemy.stun = 2
                            printWithPause(0.5, '\033[96m', f'{enemy.getPrintName()} was stunned '
                                                            f'for 2 turns by the stun grenade.')

        self.basicAttack(target, number, enemies, player)

    def actAsAlienDoctor(self, target, number, enemies, player):
        if not self.stun:
            if self.possessed:
                player.hp += 5
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} regenerated 5 hp of you')

            elif percentChance(50):
                for enemy in enemies:
                    if enemy.type in ['alien warrior', 'sun priest']:
                        enemy.hp += 3
                        printWithPause(0.5, '\033[96m', f'{self.getPrintName()} regenerated 3 hp of '
                                                        f'{enemy.getPrintName()}.')
                        break

    def actAsAlienPriest(self, target, number, enemies, player):
        if not self.stun:
            if (percentChance(33) and len([enemy for enemy in enemies if
                                           enemy.type in ['alien worshipper', 'alien cardinal']]) <= 1 and
                    self.recentSummonQty < 3):
                self.newFoes.append(foe('alien worshipper', number, scanned=1))
                number += 1
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].getPrintName()}.')
                self.recentSummonQty += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsAlienBishop(self, target, number, enemies, player):
        if not self.stun:
            if (percentChance(33) and len([enemy for enemy in enemies if
                                           enemy.type in ['alien worshipper', 'alien cardinal']]) <= 1 and
                    self.recentSummonQty < 3):
                self.newFoes.append(foe('alien cardinal', number, scanned=1))
                number += 1
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].getPrintName()}.')
                self.recentSummonQty += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsStrongerDrone(self, target, number, enemies, player):
        if not self.stun:
            self.gunWeakness = 0

            if self.possessed:
                try:
                    attackedFoe = random.choice([enemy for enemy in enemies if not enemy.possessed])
                    attackedFoe.hp -= self.attack
                    printWithPause(0.5, '\033[93m', f'{self.fullName} attacked '
                                                    f'{attackedFoe.fullName}, inflicting {self.attack} damage.')

                except IndexError:
                    pass

            else:
                player.hp -= self.attack
                printWithPause(0.5, '\033[31m', f'{self.fullName} hit you, inflicting {self.attack} '
                                                f'damage.')

        else:
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is stunned.')
            self.stun -= 1
            self.gunWeakness = 1

    def actAsAlienAdmiral(self, target, number, enemies, player):
        otherFoes = [enemy for enemy in enemies if not enemy.possessed]

        if ((not self.possessed or len(otherFoes) > 1) and (not self.stun and percentChance(33)) and
                self.recentSummonQty < 4):
            self.newFoes.append(foe('drone', number, scanned=1,
                                    possessed=self.possessed, givesPotions=0))
            printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                            f'{self.newFoes[-1].fullName}.')
            self.recentSummonQty += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()
        
    def actAsAlienNun(self, target, number, enemies, player):
        if not self.stun:
            self.cooldown -= 1
            self.twirlingNunchucks = 0
            self.damageReduction = 0

            if self.cooldown <= 0:
                self.cooldown = 3
                self.twirlingNunchucks = 1
                self.damageReduction = 0
                printWithPause(0.5, '\033[96m', f'{self.fullName} is twirling their nunchucks.')

        self.basicAttack(target, number, enemies, player)

    def actAsAlienCommander(self, target, number, enemies, player):
        if not self.stun:
            if self.recentSummonQty < 7:
                if self.hp <= 67 and percentChance(33):
                    self.newFoes.append(foe('alien attacker', number, scanned=self.scanned, givesPotions=0))
                    number += 1
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned alien attacker '
                                                    f'{number - 1} to attack you.')
                    self.recentSummonQty += 1

                if percentChance(33):
                    self.newFoes.append(foe('drone', number, scanned=self.scanned, givesPotions=0))
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned drone {number} '
                                                    f'to attack you.')
                    number += 1
                    self.recentSummonQty += 1

        if self.hp <= 133 and self.timesSummoned == 0:
            self.newFoes.append(foe('alien protector', number, scanned=self.scanned, givesPotions=0))
            number += 1
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned alien protector '
                                            f'{number - 1} to protect the commander.')
            self.timesSummoned = 1

        if self.hp <= 67 and self.timesSummoned < 2:
            self.newFoes.append(foe('alien protector', number, scanned=self.scanned, givesPotions=0))
            number += 1
            self.newFoes.append(foe('idol', number, scanned=self.scanned, givesPotions=0))
            number += 1
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned alien protector '
                                            f'{number - 2} to protect the commander.')
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned idol {number - 1} '
                                            f'to attack you.')
            self.timesSummoned = 2

        if [enemy for enemy in enemies if enemy.type == 'alien protector']:
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is immune to damage.')

            if self.bleedingDamage:
                printWithPause(0.5, '\033[96m', f"{self.getPrintName()}'s bleeding has stopped.")
                self.bleedingDamage = 0

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsAlienPilot(self, target, number, enemies, player):
        if not self.stun:
            if ((self.hp > 125 and percentChance(25)) or (self.hp <= 125 and percentChance(50))
                    and self.recentSummonQty < 2):
                foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                              'alien general', 'alien henchman']
                self.newFoes.append(foe(random.choice(foeChoices), number,
                                        scanned=self.scanned, givesPotions=0, isSummon=1))
                printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                                f'{self.newFoes[-1].getPrintName()}.')
                number += 1
                self.recentSummonQty += 1

            if ((self.hp <= 375 and self.timesSummoned == 0) or (self.hp <= 250
                                                                 and self.timesSummoned <= 1)):

                for i in range(3):
                    foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                                  'alien general', 'alien henchman']
                    self.newFoes.append(foe(random.choice(foeChoices), number,
                                            scanned=self.scanned, givesPotions=0, isSummon=1))
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                                    f'{self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.timesSummoned += 1

            elif self.hp <= 125 and self.timesSummoned <= 2:
                for i in range(3):
                    foeChoices = ['alien assassin', 'alien minion', 'alien scientist',
                                  'alien general', 'alien henchman']
                    self.newFoes.append(foe(random.choice(foeChoices), number,
                                            scanned=self.scanned, givesPotions=0, isSummon=1))
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                                    f'{self.newFoes[-1].getPrintName()}.')
                    number += 1
                    self.timesSummoned += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsAlienWarrior(self, target, number, enemies, player):
        if not self.stun:
            self.cooldown -= 1

            if self.cooldown == 1:
                self.cooldown = 0

                if self.nextAttack == 'summon':
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is preparing to summon foes.')

                elif self.nextAttack == 'explosion':
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is preparing a grenade.')

                elif self.nextAttack == 'regen':
                    printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is preparing to summon '
                                                    f'doctors.')

            elif self.cooldown < 1:
                self.cooldown = 3

                if self.nextAttack == 'summon':
                    for i in range(2):
                        nextFoe = random.choice(['alien assassin', 'idol', 'alien soldier',
                                                 'alien combat scientist'])
                        self.newFoes.append(foe(nextFoe, number, scanned=self.scanned, isSummon=1, givesPotions=0))
                        printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                                        f'{self.newFoes[-1].getPrintName()}.')
                        number += 1

                    self.nextAttack = 'regen'

                elif self.nextAttack == 'regen':
                    for i in range(3):
                        self.newFoes.append(foe('alien doctor', number, scanned=self.scanned, isSummon=1,
                                                givesPotions=0))
                        printWithPause(0.5, '\033[96m', f'{self.getPrintName()} summoned '
                                                        f'{self.newFoes[-1].getPrintName()}.')
                        number += 1
                        self.nextAttack = 'explosion'

                elif self.nextAttack == 'explosion':
                    damageToPro = getReducedDamage(40, target)
                    target.hp -= damageToPro
                    printWithPause(0.5, '\033[31m', f'You were hit by an explosion, inflicting '
                                                    f'{damageToPro} damage.')

                    for enemy in enemies:
                        enemy.hp -= 40
                        printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} was hit by an '
                                                        f'explosion, inflicting 40 damage.')

                    self.nextAttack = 'summon'

        self.basicAttack(target, number, enemies, player)

    def actAsSunPriestPt1(self, target, number, enemies, player):
        if not self.stun:
            if self.recentSummonQty < 1 and percentChance(12):
                self.newFoes.append(foe(random.choice(['alien gangster', 'alien cultist']),
                                        number, scanned=1, isSummon=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.newFoes.append(foe(random.choice(['alien nun', 'alien priest']),
                                        number, scanned=1, loot={}))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.recentSummonQty += 1

            if self.recentSummonQty < 1 and percentChance(12):
                for i in range(3):
                    self.newFoes.append(foe(random.choice(['alien colonist', 'alien bodyguard', 'alien police',
                                                           'alien soldier', 'alien secret service']), number,
                                            scanned=1, loot={}))
                    number += 1
                    printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                    f'{self.newFoes[-1].fullName}.')
                    self.recentSummonQty += 1

            if self.hp <= 2800 and self.timesSummoned == 0:
                self.newFoes.append(foe('alien bishop', number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.newFoes.append(foe('alien worshipper', number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.timesSummoned = 1

            elif self.hp <= 2600 and self.timesSummoned <= 1:
                self.newFoes.append(foe('alien bishop', number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.newFoes.append(foe('alien gangster', number, scanned=1, loot={}))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.newFoes.append(foe('alien worshipper', number, scanned=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.timesSummoned = 2

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsSunPriestPt2(self, target, number, enemies, player):
        if self.lastPtAttackMethodUsed == 1:
            self.lastPtAttackMethodUsed = 2
            printWithPause(0.5, '\033[96m', 'The sun priest is changing its strategy.')

        if not self.stun:
            self.cooldown -= 1

            if self.cooldown == 1:
                self.cooldown = 0

                if self.nextAttack == 'summon':
                    printWithPause(0.5, '\033[96m', f'{self.fullName} is preparing to summon foes.')

                elif self.nextAttack == 'explosion':
                    printWithPause(0.5, '\033[96m', f'{self.fullName} is preparing a grenade.')

                elif self.nextAttack == 'regen':
                    printWithPause(0.5, '\033[96m', f'{self.fullName} is preparing to '
                                                    f'summon doctors.')

            elif self.cooldown < 1:

                if self.nextAttack == 'summon':
                    foeChoices = (['alien gangster'] * 4 + ['alien cultist'] * 2 +
                                  ['alien worshipper'] * 3 + ['alien biologist'])

                    for i in range(3):
                        nextFoe = random.choice(foeChoices)
                        foeChoices.remove(nextFoe)
                        self.newFoes.append(foe(nextFoe, number, scanned=1, isSummon=1))
                        printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                        f'{self.newFoes[-1].fullName}.')
                        number += 1

                    self.nextAttack = 'regen'
                    self.cooldown = 5

                elif self.nextAttack == 'regen':
                    for i in range(5):
                        self.newFoes.append(foe('alien doctor', number, scanned=1))
                        printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                       f'{self.newFoes[-1].fullName}.')
                        number += 1

                    self.newFoes.append(foe('alien cultist', number, scanned=1, isSummon=1))
                    printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                   f'{self.newFoes[-1].fullName}.')
                    number += 1
                    self.newFoes.append(foe(random.choice(['alien gangster', 'alien cultist']),
                                            number, scanned=1, isSummon=1))
                    number += 1
                    printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                   f'{self.newFoes[-1].fullName}.')

                    self.nextAttack = 'explosion'
                    self.cooldown = 5

                elif self.nextAttack == 'explosion':
                    damageToPro = getReducedDamage(40, target)
                    target.hp -= damageToPro
                    printWithPause(0.5, '\033[31m', f'You were hit by an explosion, '
                                                    f'inflicting {damageToPro} damage.')

                    if 'drone' in player.inventory:
                        printWithPause(0.5, '\033[31m', 'Your drone was hit by an explosion, '
                                                        'inflicting 40 damage.')
                        player.drone.hp -= 40

                    for enemy in enemies:
                        enemy.hp -= 40
                        printWithPause(0.5, '\033[93m', f'{enemy.getPrintName()} was hit by an '
                                                        f'explosion, inflicting 40 damage.')

                    self.nextAttack = 'summon'
                    self.cooldown = 2

        self.basicAttack(target, number, enemies, player)

    def actAsSunPriestPt3(self, target, number, enemies, player):
        if self.lastPtAttackMethodUsed < 3:
            self.lastPtAttackMethodUsed = 3
            self.timesSummoned = 0
            printWithPause(0.5, '\033[96m', 'The sun priest is changing its strategy.')

        if not self.stun:
            if percentChance(35) and self.recentSummonQty < 3:
                self.newFoes.append(foe(random.choice(['alien admiral', 'alien biologist', 'alien hitman']),
                                        number, scanned=1, isSummon=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.recentSummonQty += 1

            if percentChance(35) and self.recentSummonQty < 3:
                self.newFoes.append(foe(random.choice(['alien minion', 'alien henchman', 'alien cultist']),
                                        number, scanned=1, isSummon=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.recentSummonQty += 1

            if self.timesSummoned == 0 and self.hp <= 1000:
                self.timesSummoned += 1

                for i in range(3):
                    self.newFoes.append(foe(random.choice(['alien admiral', 'alien biologist', 'alien hitman']),
                                            number, scanned=1, isSummon=1))
                    printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                    f'{self.newFoes[-1].fullName}.')
                    number += 1

            elif self.timesSummoned < 2 and self.hp <= 500:
                self.timesSummoned += 1
                self.newFoes.append(foe('alien gangster', number, scanned=1, loot={}))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1
                self.newFoes.append(foe('alien cultist', number, scanned=1, isSummon=1))
                printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                f'{self.newFoes[-1].fullName}.')
                number += 1

                for i in range(3):
                    self.newFoes.append(foe(random.choice(['alien admiral', 'alien biologist', 'alien hitman']),
                                            number, scanned=1, isSummon=1))
                    printWithPause(0.5, '\033[96m', f'{self.fullName} summoned '
                                                    f'{self.newFoes[-1].fullName}.')
                    number += 1
                    self.timesSummoned += 1

        self.basicAttack(target, number, enemies, player)
        self.handleRecentSummonQty()

    def actAsSunPriest(self, target, number, enemies, player):
        if self.hp > 2400:
            self.actAsSunPriestPt1(target, number, enemies, player)

        elif self.hp > 1500:
            self.actAsSunPriestPt2(target, number, enemies, player)

        else:
            self.actAsSunPriestPt3(target, number, enemies, player)

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
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} is immune to stun.')

    def getPrintName(self):
        return self.fullName if self.scanned else '???'

    def actAsFoe(self, target, number, enemies, protagonist):
        self.getDamage(enemies)

        if self.hp > 0:
            self.attackMethod(target, number, enemies, protagonist)

        self.getHurtByDebuffs(protagonist)

    def getUpdate(self):
        pass

    def beHitByBaton(self):
        self.hitsUntilStunnedByBaton -= 1

        if self.hitsUntilStunnedByBaton <= 0:
            self.stun += 2
            self.hitsUntilStunnedByBaton = 5
            printWithPause(0.5, '\033[96m', f'{self.getPrintName()} was stunned by your baton.')
