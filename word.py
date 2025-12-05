import pygame

from variables import display

pygame.font.init()


class Word:
    def __init__(self, text, left, top, color=(200, 237, 255), background=(0, 0, 0), font='Times', size=24,
                 isBold=False, isItalic=False):
        self.text = text
        self.left = left
        self.top = top
        self.font = pygame.font.SysFont(font, size, bold=isBold, italic=isItalic)
        self.sprite = self.font.render(self.text, False, color, background)
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.bottom = top + self.height

    def draw(self, yShift=0):
        """Draws self to the display."""

        display.blit(self.sprite, (self.left, self.top + yShift))