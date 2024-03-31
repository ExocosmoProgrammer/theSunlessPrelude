import random

from definitions import percentChance, betterRange, sign, greater
from variables import movementPuzzleFoeSprites, keysPerDirection
from movementPuzzleFireball import movementPuzzleFireball


class movementPuzzleFoe:
    def __init__(self, coordinate, kind, board):
        if kind == 'charging':
            self.speed = 2

        elif kind == 'alien pilot':
            self.speed = 0

        else:
            self.speed = 1

        if kind == 'mysterious figure':
            self.drones = [movementPuzzleFoe(coord, 'drone', board) for coord in [[0, 0], [8, 0], [4, 2]]]

        self.type = kind
        self.coordinate = coordinate
        self.tilesSkipped = []
        self.availableDirections = []
        self.getDirections(board)
        self.direction = random.choice(self.availableDirections)
        self.lastDirection = self.direction.copy()
        actionsPerFoe = {'basic': self.move, 'charging': self.actAsChargingFoe, 'mage': self.actAsMage,
                         'alien pilot': self.actAsAlienPilot, 'alien warrior': self.actAsAlienWarrior,
                         'sun priest': self.actAsSunPriest, 'drone': self.actAsDrone,
                         'mysterious figure': self.actAsMysteriousFigure}
        self.action = actionsPerFoe[kind]
        self.fireballs = []
        self.cooldown = 0
        self.destination = [4, 8]
        self.lastDestination = [4, 8]
        self.destinationReached = 1
        self.lastDestinationProcedure = 0
        self.destinationProcedure = 0

    def getDirections(self, board):
        self.availableDirections = []

        for i in [[-self.speed, 0], [self.speed, 0], [0, -self.speed], [0, self.speed]]:
            newLocation = (self.coordinate[0] + sign(i[0]), self.coordinate[1] + sign(i[1]))

            if newLocation in board.keys() and board[tuple(newLocation)] in ['     ', '  i  '] and \
                    board[(self.coordinate[0] + sign(i[0]), self.coordinate[1] + sign(i[1]))] != ' ||| ':
                self.availableDirections.append(i)

    def reverseLastDirection(self):
        return [-self.lastDirection[0], -self.lastDirection[1]]

    def checkLineOfSightWithPlayer(self, board, playerSpace):
        if self.coordinate[0] == playerSpace[0] and ' ||| ' not in [board[(playerSpace[0], i)] for i in \
                                                                    betterRange(self.coordinate[1], playerSpace[1])]:
            return 1

        elif self.coordinate[1] == playerSpace[1] and ' ||| ' not in [board[(i, playerSpace[1])] for i in \
                                                                      betterRange(self.coordinate[0], playerSpace[0])]:
            return 1

        return 0
    
    def checkLineOfSightWithFoe(self, board, coord):
        if self.coordinate[0] == coord[0] and ' ||| ' not in [board[(coord[0], i)] for i in \
                                                                    betterRange(self.coordinate[1], coord[1])]:
            return 1

        elif self.coordinate[1] == coord[1] and ' ||| ' not in [board[(i, coord[1])] for i in \
                                                                      betterRange(self.coordinate[0], coord[0])]:
            return 1

        return 0

    def move(self, board, playerSpace):
        def isZero(a):
            return 1 if a == 0 else 0

        self.tilesSkipped = []
        board[tuple(self.coordinate)] = '     '

        for i in range(int(greater(abs(self.direction[0]), abs(self.direction[1])))):
            self.coordinate[0] += sign(self.direction[0])
            self.coordinate[1] += sign(self.direction[1])

            if tuple(self.coordinate) not in board.keys() or board[tuple(self.coordinate)] == ' ||| ' or \
                    type(board[tuple(self.coordinate)]) == movementPuzzleFoe:
                self.coordinate[0] -= sign(self.direction[0])
                self.coordinate[1] -= sign(self.direction[1])
                break

            if i != greater(abs(self.direction[0]), abs(self.direction[1])) - 1:
                self.tilesSkipped.append(board[tuple(self.coordinate)])

        board[tuple(self.coordinate)] = self
        newLocation = (self.coordinate[0] + sign(self.direction[0]), self.coordinate[1] + sign(self.direction[1]))
        self.getDirections(board)

        if newLocation not in board.keys() or board[tuple(newLocation)] not in ['     ', '  i  '] or \
                self.direction == [0, 0]:
            if not self.availableDirections:
                lastDirection = self.direction.copy()
                newDirection = [0, 0]

            elif self.availableDirections == [[-self.direction[0], -self.direction[1]]]:
                newDirection = [-self.direction[0], -self.direction[1]]
                lastDirection = self.direction.copy()

            else:
                newDirection = random.choice([direction for direction in self.availableDirections if direction != \
                                              [-self.direction[0], -self.direction[1]]])

            lastDirection = self.direction.copy()
            self.direction = newDirection
            self.lastDirection = lastDirection

        elif len(self.availableDirections) > 2:
            if percentChance(50) and not \
                    (self.type == 'alien warrior' and self.checkLineOfSightWithPlayer(board, playerSpace)):
                newDirection = random.choice([direction for direction in self.availableDirections if direction not in \
                                              [[-self.direction[0], -self.direction[1]], self.direction]])
                lastDirection = self.direction.copy()
                self.direction = newDirection
                self.lastDirection = lastDirection

            elif self.type not in ['alien warrior', 'charging']:
                warriors = [enemy for enemy in [i for i in board.values() if type(i) == movementPuzzleFoe] if \
                           enemy.type == 'alien warrior']

                if warriors:
                    warrior = warriors[0]

                    if self.checkLineOfSightWithFoe(board, warrior.coordinate) and not \
                            (isZero(self.coordinate[0]) != isZero(warrior.coordinate[0]) and \
                             isZero(self.coordinate[1]) != isZero(warrior.coordinate[1])):
                        newDirection = random.choice(
                            [direction for direction in self.availableDirections if direction not in \
                             [[-self.direction[0], -self.direction[1]], self.direction]])
                        lastDirection = self.direction.copy()
                        self.direction = newDirection
                        self.lastDirection = lastDirection

        return board

    def actAsChargingFoe(self, board, playerSpace):
        self.tilesSkipped = []

        if self.checkLineOfSightWithPlayer(board, playerSpace):
            self.direction = [2 * sign(playerSpace[0] - self.coordinate[0]), 2 * \
                              sign(playerSpace[1] - self.coordinate[1])]
            board = self.move(board, playerSpace)

        return board

    def actAsMage(self, board, playerSpace):
        board = self.move(board, playerSpace)
        self.cooldown -= 1

        if self.cooldown <= 0 and self.checkLineOfSightWithPlayer(board, playerSpace) and \
                self.coordinate != playerSpace:
            pathToPlayer = [sign(playerSpace[0] - self.coordinate[0]), sign(playerSpace[1] - self.coordinate[1])]
            self.fireballs.append(movementPuzzleFireball(self.coordinate.copy(), pathToPlayer[0], pathToPlayer[1]))
            self.cooldown = 7

        return board

    def actAsAlienPilot(self, board, playerSpace):
        return board

    def __str__(self):
        try:
            return '\033[91m' + movementPuzzleFoeSprites[self.type][keysPerDirection[(sign(self.direction[0]), \
                                                                                      sign(self.direction[1]))]]

        except KeyError:
            return '\033[91m' + movementPuzzleFoeSprites[self.type]['s']

    def actAsAlienWarrior(self, board, playerSpace):
        if self.checkLineOfSightWithPlayer(board, playerSpace):
            self.cooldown -= 1
            self.direction = [sign(playerSpace[0] - self.coordinate[0]), sign(playerSpace[1] - self.coordinate[1])]

            if self.cooldown <= 0:
                self.speed = 2

        else:
            self.cooldown = 3
            self.speed = 1

        for i in range(2):
            self.direction[i] *= self.speed

        x = self.move(board, playerSpace)
        return x

    def actAsSunPriest(self, board, playerSpace):
        x = self.move(board, playerSpace)
        self.cooldown -= 1

        if self.cooldown <= 0:
            self.cooldown = 11

            if self.fireballs:
                fireballLocations = [fireball.coordinate for fireball in self.fireballs if not fireball.hurts]
                self.fireballs = []

                for coordinate in fireballLocations:
                    self.fireballs.append(movementPuzzleFireball(coordinate, 0, 0, linger=5))

            for i in range(4):
                coordinate = [random.randint(0, 7), random.randint(0, 7)]

                for i in range(2):
                    for j in range(2):
                        self.fireballs.append(movementPuzzleFireball([coordinate[0] + i, coordinate[1] + j],
                                                                     0, 0, harmful=False, sprite=' !!! '))

        return x

    def actAsMysteriousFigure(self, board, playerSpace):
        def isEven(a):
            return 0 if a % 2 else 1

        escapes = [key for key in board.keys() if board[key] != ' ||| ' and not isEven(key[1])]

        for enemy in [enemy for enemy in self.drones]:
            distanceToPro = abs(enemy.coordinate[1] - playerSpace[1])

            if isEven(enemy.coordinate[1]):
                if enemy.checkLineOfSightWithPlayer(board, playerSpace):
                    enemy.destination = [enemy.coordinate[0] + sign(playerSpace[0] - enemy.coordinate[0]),
                                         enemy.coordinate[1] + sign(playerSpace[1] - enemy.coordinate[1])]
                    enemy.destinationProcedure = 1

                elif distanceToPro > 3:
                    potentialEscapes = [escape for escape in escapes if abs(escape[1] - enemy.coordinate[1]) == 1 and \
                                        sign(escape[1] - enemy.coordinate[1]) == \
                                        sign(playerSpace[1] - enemy.coordinate[1])]
                    distancesPerEscape = {}

                    for escape in potentialEscapes:
                        distancesPerEscape[escape] = abs(enemy.coordinate[0] - escape[0]) + \
                                                     abs(enemy.coordinate[1] - escape[1])

                    enemy.destination = [key for key in potentialEscapes if distancesPerEscape[key] == \
                                        min(distancesPerEscape.values())][0]
                    escapes.remove(enemy.destination)
                    enemy.destinationProcedure = 2

                elif distanceToPro > 1:
                    playerEscapes = [key for key in board.keys() if abs(key[1] - playerSpace[1]) <= 2 and board[key] != \
                                     ' ||| ' and not isEven(key[1]) and sign(key[1] - playerSpace[1]) == \
                                     sign(enemy.coordinate[1] - playerSpace[1]) and key in escapes]
                    nearestPlayerEscapes = []
                    enemy.destinationProcedure = 3

                    try:
                        nearestPlayerEscapes.append((max(i[0] for i in playerEscapes if i[0] < playerSpace[0]),
                                                     playerEscapes[0][1]))

                    except ValueError:
                        try:
                            enemy.destination = (min([i[0] for i in playerEscapes if i[0] > playerSpace[0]]),
                                                 playerEscapes[0][1])

                        except ValueError:
                            pass

                    try:
                        nearestPlayerEscapes.append((min([i[0] for i in playerEscapes if i[0] > playerSpace[0]]),
                                                     playerEscapes[0][1]))

                    except ValueError:
                        try:
                            enemy.destination = (max(i[0] for i in playerEscapes if i[0] < playerSpace[0]),
                                                 playerEscapes[0][1])

                        except ValueError:
                            pass

                    if len(nearestPlayerEscapes) > 1:
                        if abs(enemy.coordinate[0] - nearestPlayerEscapes[0][0]) + \
                                abs(enemy.coordinate[1] - nearestPlayerEscapes[0][1]) < \
                                abs(enemy.coordinate[0] - nearestPlayerEscapes[1][0]) + \
                                abs(enemy.coordinate[1] - nearestPlayerEscapes[1][1]):
                            enemy.destination = nearestPlayerEscapes[0]

                        else:
                            enemy.destination = nearestPlayerEscapes[1]

                else:
                    enemy.destination = [enemy.coordinate[0] + sign(playerSpace[0] - enemy.coordinate[0]),
                                         enemy.coordinate[1] + sign(playerSpace[1] - enemy.coordinate[1])]
                    enemy.destinationProcedure = 4

            elif enemy.coordinate[1] == playerSpace[1]:
                enemy.destination = (enemy.coordinate[0], enemy.coordinate[1] - 1)
                enemy.destinationProcedure = 5

            else:
                enemy.destination = (enemy.coordinate[0],
                                    enemy.coordinate[1] + sign(playerSpace[1] - enemy.coordinate[1]))
                enemy.destinationProcedure = 6

        for enemy in self.drones:
            board = enemy.actAsDrone(board, playerSpace)

        return board

    def actAsDrone(self, board, playerSpace):
        if self.lastDestinationProcedure == self.destinationProcedure and not self.destinationReached:
            self.destination = self.lastDestination

        else:
            self.lastDestination = self.destination

        self.lastDestinationProcedure = self.destinationProcedure

        if self.destination[1] == self.coordinate[1] or self.destination[0] == self.coordinate[0] and \
                self.checkLineOfSightWithFoe(board, self.destination):
            self.direction = [sign(self.destination[0] - self.coordinate[0]),
                              sign(self.destination[1] - self.coordinate[1])]

        elif self.destination[1] != self.coordinate[1] and \
                board[(self.coordinate[0],
                       self.coordinate[1] + sign(self.destination[1] - self.coordinate[1]))] != ' ||| ':
            self.direction = [0, sign(self.destination[1] - self.coordinate[1])]

        else:
            self.direction = [sign(self.destination[0] - self.coordinate[0]), 0]

        x = self.move(board, playerSpace)

        if self.coordinate == self.destination:
            self.destinationReached = 1

        return x
