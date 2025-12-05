import pygame.event

from word import Word
from variables import WIDTH, HEIGHT


class Text:
    def __init__(self, text: str, left=0, bottom=HEIGHT, maxRight=WIDTH, color=(200, 237, 255), background=(0, 0, 0),
                 font='Times', size=24, spacing=6, lineSpacing=24, isBold=False, isItalic=False, topShown=0,
                 bottomShown = HEIGHT):
        self.topShown = topShown
        self.text = text
        self.color = color
        self.background = background
        self.font = font
        self.size = size
        self.spacing = spacing
        self.lineSpacing = lineSpacing
        self.isBold = isBold
        self.isItalic = isItalic
        self.topShown = topShown
        self.bottomShown = bottomShown

        # Get the words in self.
        wordList = text.split()
        self.words = []

        currentRight = left
        currentTop = 0

        for i in wordList:
            # Create a new word to add.
            newWord = Word(i, currentRight, currentTop, color=color, background=background, font=font, size=size,
                           isBold=isBold, isItalic=isItalic)

            # If the word would go off the screen, then go down to the next line.
            if currentRight + newWord.width > maxRight:
                currentRight = left
                currentTop += lineSpacing
                newWord.left = left
                newWord.top = currentTop
                newWord.height = newWord.sprite.get_height()
                newWord.bottom = currentTop + newWord.height

            # Add the new word.
            self.words.append(newWord)

            # Update currentRight. Since there should be a space between words, add extra space.
            currentRight += spacing + newWord.width

        # Shift the words in self so that the bottom of self is actually at bottom.
        yShift = bottom - (self.words[-1].top + self.words[-1].height)

        for i in self.words:
            i.top += yShift
            i.bottom += yShift

        # Get self's top, bottom, and height.
        self.top = self.words[0].top
        self.bottom = self.words[-1].bottom
        self.height = self.bottom - self.top

    def draw(self, yShift=0):
        """Draws self."""

        for i in self.words:
            # Words that are too high or low are not drawn. This is useful for drawing displays.
            if i.top + yShift >= self.topShown and i.bottom + yShift <= self.bottomShown:
                i.draw(yShift)


