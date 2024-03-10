import random

from definitions import percentChance, betterRange, sign, greater
from variables import movementPuzzleFoeSprites, keysPerDirection
from movementPuzzleFireball import movementPuzzleFireball


class movementPuzzleFoe:
    def __init__(self, coordinate, kind, board):
        self.type = kind

        if kind in ['basic', 'mage']:
            self.speed = 1

        elif kind == 'charging':
            self.speed = 2

        self.coordinate = coordinate
        self.tilesSkipped = []
        self.availableDirections = []
        self.getDirections(board)
        self.direction = random.choice(self.availableDirections)
        self.lastDirection = self.direction.copy()
        actionsPerFoe = {'basic': self.move, 'charging': self.actAsChargingFoe, 'mage': self.actAsMage}
        self.action = actionsPerFoe[kind]
        self.fireballs = []
        self.fireCooldown = 0

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

    def move(self, board, playerSpace):
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

        elif len(self.availableDirections) > 2 and percentChance(50):
            newDirection = random.choice([direction for direction in self.availableDirections if direction not in \
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
        self.fireCooldown -= 1

        if self.fireCooldown <= 0 and self.checkLineOfSightWithPlayer(board, playerSpace) and \
                self.coordinate != playerSpace:
            pathToPlayer = [sign(playerSpace[0] - self.coordinate[0]), sign(playerSpace[1] - self.coordinate[1])]
            self.fireballs.append(movementPuzzleFireball(self.coordinate.copy(), pathToPlayer[0], pathToPlayer[1]))
            self.fireCooldown = 7

        return board

    def __str__(self):
        try:
            return '\033[91m' + movementPuzzleFoeSprites[self.type][keysPerDirection[(sign(self.direction[0]), \
                                                                                      sign(self.direction[1]))]]

        except KeyError:
            return '\033[91m' + movementPuzzleFoeSprites[self.type]['s']
