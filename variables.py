foesPerLevel = {1: ['alien colonist', 'alien bodyguard', 'alien police', 'alien soldier',
                    'alien secret service'],
                2: ['alien assassin', 'alien minion', 'alien general', 'alien scientist',
                    'alien henchman'],
                3: ['alien combat scientist', 'alien assassin', 'alien minion'],
                4: ['alien priest', 'alien gangster', 'alien cultist', 'alien nun']}
hpPerFoe = {'alien colonist': 10, 'alien bodyguard': 20, 'alien police': 30,
            'alien soldier': 40, 'alien secret service': 50, 'alien commander': 200,
            'alien attacker': 10, 'alien protector': 50, 'drone': 10, 'idol': 30,
            'alien assassin': 10, 'alien minion': 30, 'alien general': 50,
            'alien scientist': 60, 'alien henchman': 75, 'alien pilot': 500,
            'alien combat scientist': 30, 'alien warrior': 750, 'alien doctor': 10,
            'alien priest': 30, 'alien worshipper': 1, 'alien gangster': 40,
            'alien cultist': 40, 'alien nun': 50, 'sun priest': 3000, 'alien bishop': 50,
            'alien cardinal': 1, 'alien admiral': 50, 'stronger drone': 10, 'alien biologist': 50,
            'alien hitman': 20, 'alien mobster': 40, 'the sun': 100000, 'alien mother superior': 50,
            'alien devotee': 50, 'helpless sun priest': 50}
attackPerFoe = {'alien colonist': 2, 'alien bodyguard': 3, 'alien police': 6,
                'alien soldier': 7, 'alien secret service': 8, 'alien commander': 5,
                'alien attacker': 15, 'alien protector': 0, 'drone': 3, 'idol': 5,
                'alien assassin': 15, 'alien minion': 7, 'alien general': 7,
                'alien scientist': 10, 'alien henchman': 12, 'alien pilot': 10,
                'alien combat scientist': 10, 'alien warrior': 20, 'alien doctor': 5,
                'alien priest': 5, 'alien worshipper': 1, 'alien gangster': 15,
                'alien cultist': 7, 'alien nun': 7, 'sun priest': 10, 'alien bishop': 5,
                'alien cardinal': 15, 'alien admiral': 7, 'stronger drone': 3, 'alien biologist': 10,
                'alien hitman': 20, 'alien mobster': 20, 'the sun': 40, 'alien mother superior': 7,
                'alien devotee': 10, 'helpless sun priest': 0}
lootPerFoe = {'alien colonist': {'regen': 7}, 'alien bodyguard': {'shield': 7},
              'alien police': {'baton': 7}, 'alien soldier': {'knife': 7},
              'alien secret service': {'gun': 7}, 'alien assassin': {'stun grenade': 100,
                                                                     'gas canister': 7},
              'alien minion': {'throwing knife': 100, 'radio': 7},
              'alien scientist': {'solution': 100, 'combustible lemon': 1, 'hissing cockroach': 7},
              'alien general': {'sword': 50, 'drone': 7},
              'alien henchman': {'armor': 50, 'serrated knife': 100, 'vial of diseased blood': 7},
              'alien combat scientist': {'solution': 100, 'combustible lemon': 1, 'hissing cockroach': 7},
              'alien doctor': {'solution': 50, 'throwing knife': 50},
              'alien cultist': {'vial of poison': 100, 'sacrificial dagger': 15}, 'alien nun': {'nunchucks': 15},
              'alien priest': {'cross': 15}, 'alien gangster': {'butterfly knife': 15},
              'alien biologist': {'solution': 100, 'combustible lemon': 1, 'hissing cockroach': 25},
              'alien admiral': {'sword': 50, 'drone': 25},
              'alien hitman': {'stun grenade': 100, 'gas canister': 25},
              'alien bishop': {'cross': 25}, 'alien mother superior': {'nunchucks': 25},
              'alien devotee': {'vial of poison': 100, 'sacrificial dagger': 25},
              'alien mobster': {'butterfly knife': 25}}
descriptionPerFoe = {'alien colonist': 'The colonists are aliens who were selected for military service but '
                                       'considered poor at fighting. They stay behind the army and build civilizations '
                                       'for the aliens.',
                     'alien bodyguard': 'The bodyguards are alien soldiers that stick with important members of the '
                                        'alien army.',
                     'alien police': 'The police are alien soldiers that enforce the rules of the alien military.',
                     'alien soldier': 'The alien soldiers make up most of the alien army. They are insignificant '
                                      'fighters.',
                     'alien secret service': 'The secret service get information for the sun priest.',
                     'alien commander': 'The commanders have control over groups of troops.',
                     'drone': 'The drones are machines that were designed to assist the alien armies.',
                     'idol': 'The idols are machines that were designed to represent a God and to assist the '
                             'alien armies.',
                     'alien protector': 'The protectors serve only to prevent important members of the alien army from '
                                        'being harmed.',
                     'alien attacker': 'The attackers attack anyone who is considered a threat to important members of '
                                       'the alien army.',
                     'alien assassin': 'The assassins are hired by higher up commanders and pilots to kill specific '
                                       'targets.',
                     'alien minion': 'The minions are members of the alien army. They perform chores for the army but '
                                     'do not usually fight.',
                     'alien general': 'The generals command disposable troops, which are prominently drones.',
                     'alien scientist': 'The alien scientists are in charge of creating technology to help the alien '
                                        'army.',
                     'alien henchman': 'The henchmen are members of the alien army. They perform chores for the army.',
                     'alien pilot': 'The pilots fly ships. The pilots also tend to excel in combat.',
                     'alien combat scientist': 'The combat scientists create technology, which they use to fight.',
                     'alien warrior': 'There are rumors of an elite group of scientists that specialize in '
                                      'biomechanical enhancements. Said scientists are credited for the rise of many '
                                      'elite soldiers. \n\n\n"We love you, be safe -Mom & Dad"',
                     'alien doctor': 'The doctors are in charge of treating injuries of members of the alien army. ',
                     'alien priest': 'Civilian priests who are famed for their church services.',
                     'alien worshipper': 'Devoted members of a religion. They would likely even die for it.',
                     'alien gangster': 'Members of a prominent and controversial gang. Known to protect their '
                                       'communities from outside dangers.',
                     'alien cultist': 'A mysterious group that sacrifices humans in the name of warding off a '
                                      'darkness.',
                     'alien nun': 'The nuns are hired to keep undesirables out of the many churches across earth.',
                     'alien bishop': 'The bishops act as a medium for the sun priest to influence the church from'
                                     'behind the scenes.',
                     'alien cardinal': 'The cardinals are the most extreme devotees of the church. They are '
                                       'strengthened by the sun priest and assigned to protect bishops.',
                     'alien admiral': 'Robotics is a small field on earth, with many choosing to join the army as a'
                                      'soldier or to join the church. A few become scientists, but almost none enter '
                                      'robotics. The drones that admirals command are a new model that was '
                                      'created by a young roboticist.',
                     'stronger drone': 'A new model of drone created by a prodigious scientist who is often known'
                                       ' for his disfigured face and leg. The drone is said to resemble the skull of'
                                       ' a donkey.',
                     'alien biologist': 'Members of a dangerous terrorist organization that opposes the church.'
                                        ' They are known for their use of biological warfare.',
                     'alien hitman': 'The hitmen are elite assassins that are used exclusively by admirals and '
                                     'the sun priest.',
                     'alien mobster': 'The alien mobsters are infamous gangsters from an especially violent gang.',
                     'alien mother superior': 'The mother superiors act as bodyguards for bishops and cardinals.',
                     'alien devotee': 'The devotees are infamous members of a mysterious group that sacrifices humans '
                                      'to the sun.',
                     'sun priest': 'Gods are known to change over time. The sun priest is a god of the sun and of war. '
                                   'He causes wars so that he continues to be worshipped.',
                     'the sun': 'The sun is a star that gives light to the earth. Some powerful gods have been known '
                                'to harness its power for themselves.'}
combatInfoPerFoe = {'alien commander': '[200, 67): The alien commander can directly attack you and can summon drones.\n'
                                       '[67, 0): The alien commander can directly attack you and can summon drones '
                                       'and alien attackers.\n'
                                       '133: The commander summons an alien protector.\n'
                                       '67: The commander summons an alien protector and an idol.',
                    'alien protector': 'Alien protectors make the alien commander immune to all damage.',
                    'idol': 'Idols attack every turn. They cannot be blocked or stunned.',
                    'alien assassin': 'Alien assassins may throw stun grenades. One turn before an assassin throws a '
                                      'stun grenade, you will be warned that they are preparing a stun grenade. If '
                                      'an alien assassin that is aggressive to the player throws a stun grenade, the '
                                      'player will be stunned for one turn. If an alien assassin that is on the '
                                      'player\'s side throws a stun grenade, every enemy that is aggressive to the '
                                      'player will be stunned and the alien assassin will lose 5 hp.',
                    'alien general': 'Alien generals can summon drones.',
                    'alien scientist': 'Alien scientists that are aggressive to the player can empower other enemies '
                                       'that are aggressive to the player. Empowered enemies inflict double damage '
                                       'with their regular attacks and will perform an extra, weaker, unblockable '
                                       'attack each turn. Alien scientists that are on the player\'s side can reduce '
                                       'the attack of enemies that are aggressive to the player.',
                    'alien pilot': 'The pilot can summon any other enemy type that can appear in the ship without '
                                   'being summoned. At <= 125 hp, the pilot has a greater chance to randomly summon '
                                   'an enemy each turn.\n'
                                   '375: The pilot summons three random enemies.\n'
                                   '250: The pilot summons three random enemies.\n'
                                   '125: The pilot summons three random enemies.',
                    'alien combat scientist': 'Each turn, alien combat scientists that are aggressive to the player '
                                              'will empower another enemy that is aggressive to the player if '
                                              'possible. Each turn, alien combat scientists that are on the player\'s '
                                              'side will reduce the attack of an enemy that is aggressive to the '
                                              'player if possible.',
                    'alien warrior': 'The alien warrior performs special attacks in the order of summoning two '
                                     'attackers, summoning three doctors, and throwing a grenade. The alien warrior\'s '
                                     'grenades can be blocked. They hurt every enemy and the player. If the player '
                                     'has a drone, the grenade hurts the player\'s drone.',
                    'alien doctor': 'Alien doctors that are not on the player\'s side can heal the alien warrior. '
                                    'Alien doctors that are on the player\'s side can heal the player.',
                    'alien priest': 'Alien priests can summon alien worshippers.',
                    'alien worshipper': 'If the player attacks any sort of priest or bishop when there are any alien '
                                        'worshippers or alien cardinals that are aggressive to the player, a random '
                                        'enemy that is aggressive to the player and is either an alien worshipper or '
                                        'an alien cardinal will block your attack.',
                    'alien gangster': 'Alien gangsters\' attacks cannot be blocked. The gangsters\' attacks cannot be '
                                      'reflected by nunchucks.',
                    'alien cultist': 'Alien cultists get a higher damage bonus the more alien cultists and alien '
                                     'devotees there are.',
                    'alien nun': 'Alien nuns can twirl their nunchucks. You will be warned when a nun is twirling '
                                 'their nunchucks. Nuns that are twirling their nunchucks will hurt whatever attacks '
                                 'the nuns. The nuns can reflect some one time use items.',
                    'alien bishop': 'Alien bishops can summon alien cardinals.',
                    'alien cardinal': 'If the player attacks any sort of priest or bishop when there are any alien '
                                      'worshippers or alien cardinals that are aggressive to the player, a random '
                                      'enemy that is aggressive to the player and is either an alien worshipper or '
                                      'an alien cardinal will block your attack.',
                    'alien admiral': 'Alien admirals can summon stronger drones.',
                    'stronger drone': 'Every turn, stronger drones attack unless they are stunned. They cannot be '
                                      'blocked.',
                    'alien biologist': 'Alien biologists that are aggressive to the player can empower other enemies '
                                       'that are aggressive to the player. Empowered enemies inflict double damage '
                                       'with their regular attacks and will perform an extra, weaker, unblockable '
                                       'attack each turn. Alien biologists that are on the player\'s side can reduce '
                                       'the attack of enemies that are aggressive to the player. Alien biologists '
                                       'poison enemies that the biologists attack.',
                    'alien hitman': 'Alien hitmen may throw stun grenades. One turn before an hitman throws a '
                                    'stun grenade, you will be warned that they are preparing a stun grenade. If '
                                    'an alien hitman that is aggressive to the player throws a stun grenade, the '
                                    'player will be stunned for one turn. If an alien hitman that is on the '
                                    'player\'s side throws a stun grenade, every enemy that is aggressive to the '
                                    'player will be stunned and the alien hitman will lose 5 hp.',
                    'alien mobster': 'Alien mobsters\' attacks cannot be blocked. The mobsters\' attacks cannot be '
                                      'reflected by nunchucks.',
                    'alien mother superior': 'Alien mother superiors can twirl their nunchucks. You will be warned '
                                             'when an alien mother superior is twirling their nunchucks. Alien mother '
                                             'superiors that are twirling their nunchucks will hurt whatever attacks '
                                             'the alien mother superiors. The alien mother superiors can reflect '
                                             'some one time use items. The alien mother superiors that are twirling '
                                             'their nunchucks are immune to damage that is directly from attacks.',
                    'alien devotee': 'Alien devotees get a higher damage bonus the more alien cultists and alien '
                                     'devotees there are. Alien devotees regenerate hp each turn unless they have 50 '
                                     'hp. They cannot have more than 50 hp. They heal slower the more alien cultists '
                                     'and alien devotees there are.',
                    'sun priest': '[3000, 2400): The sun priest can summon enemies from levels one and four.\n'
                                  '[2400, 1500): The sun priest performs special attacks in the order of summoning '
                                  'attackers, summoning doctors and attackers, and throwing an incendiary. The '
                                  'incendiary burns every enemy and the player. If the player has a drone, the '
                                  'incendiary burns the player\'s drone.\n'
                                  '[1500, 0): The sun priest can summon some enemies from levels two and four.\n'
                                  '2800: The sun priest summons an alien worshipper and an alien bishop.\n'
                                  '2600: The sun priest summons an alien worshipper, an alien bishop, and an alien '
                                  'gangster.\n'
                                  '1500: The sun priest summons the sun.\n'
                                  '1000: The sun priest summons three random foes.\n'
                                  '500: The sun priest summons an alien gangster, an alien cultist, and three random '
                                  'foes.',
                    'the sun': 'The sun attacks you with a consistent cooldown.'}
bestiaryOrder = ['alien colonist', 'alien bodyguard', 'alien police', 'alien soldier', 'alien secret service',
                 'alien commander', 'drone', 'alien protector', 'idol', 'alien attacker', 'alien assassin',
                 'alien minion', 'alien general', 'alien scientist', 'alien henchman', 'alien pilot',
                 'alien combat scientist', 'alien warrior', 'alien priest', 'alien worshipper', 'alien cultist',
                 'alien gangster', 'alien nun', 'alien hitman', 'alien admiral', 'alien biologist', 'alien mobster',
                 'alien bishop', 'alien cardinal', 'alien mother superior', 'alien devotee', 'sun priest', 'the sun']
for enemy in bestiaryOrder:
    if enemy not in combatInfoPerFoe.keys():
        combatInfoPerFoe[enemy] = (f'Enemies of the type type "{enemy}" have a chance to attack each turn unless said'
                                   f' enemies are stunned.')

bossesPerLevel = {1: 'alien commander', 2: 'alien pilot', 3: 'alien warrior'}
oneTimeUseItems = ['solution', 'stun grenade', 'throwing knife', 'vial of poison', 'serrated knife',
                   'combustible lemon']
textColors = [f'\033[9{i}m' for i in range(1, 8)]
songsPerLevel = {1: 'The War.mp3', 2: 'The Ship.mp3', 3: 'Doubt.mp3', 4: 'Determination .mp3'}
initialFoesPerLevel = {1: 1, 2: 1, 3: 3, 4: 0}
