import time

import pygame.event

from text import Text
from variables import display


class Display:
    def __init__(self, left, width, bottom, height, texts: list[Text], scrollModifier=0):
        self.left = left
        self.width = width
        self.right = self.left + width
        self.bottom = bottom
        self.top = bottom - height
        self.height = height

        # The texts are modified to be shown within self.
        self.texts = [Text(i.text, left=left + 6, bottom=bottom - 6, maxRight=self.right - 6, color=i.color,
                           background=i.background, font=i.font, size=i.size, spacing=i.spacing,
                           lineSpacing=i.lineSpacing, isBold=i.isBold, isItalic=i.isItalic,
                           topShown=self.top + 6, bottomShown=self.bottom - 6) for i in texts]

        # Make attributes for the border around self.
        self.outerBorderRect = pygame.Rect(self.left, self.top, self.width, self.height)
        self.innerBorderRect = pygame.Rect(self.left + 2, self.top + 2, self.width - 4, self.height - 4)

        # Text inside self is drawn with an extra vertical shift of self.scrollModifier.
        self.scrollModifier = scrollModifier

    def shift(self, xShift, yShift):
        """Shifts self horizontally by xShift and vertically by yShift."""

        self.__init__(self.left + xShift, self.width, self.bottom + yShift, self.height, self.texts.copy(),
                      scrollModifier=self.scrollModifier)

    def draw(self):
        """Draws self."""

        # Draw a border around self.
        display.fill((220, 240, 255), self.outerBorderRect)
        display.fill((0, 0, 0), self.innerBorderRect)

        # Draw the texts.
        currentYShift = 0

        # Draw each text, and modify currentYShift each time.
        for i in self.texts:
            i.draw(yShift=currentYShift + self.scrollModifier)
            currentYShift -= i.height + 8


text1 = Text('Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. Hello, world! This is a test of my new, totally '
               'awesome system for using Pygame\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. Hello, world! This is a test of my new, totally '
               'awesome system for using Pygame\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon.', left=50, bottom=800, color=(200, 200, 150),
               font='Times', lineSpacing=28, spacing=3,  isBold=True, isItalic=True, maxRight=1000)
text2 = Text('Hello, world. Here is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. Hello, world! Here is a test of my new, totally '
               'awesome system for using Pygame\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This feature will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. Hello, world! This is a test of my new, totally '
               'awesome system for using Pygame\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon.', left=50, bottom=800, color=(210, 200, 150),
               font='Times', lineSpacing=24, spacing=5,  isBold=False, isItalic=True, maxRight=1000)
text3 = Text('Hi, world! Here is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon. Hello, world! Here is a test of my new, totally '
               'awesome system for using Pygame\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This feature will be a needed feature soon. '
               'Hello, world! T\'s font module to draw text. This will be a needed feature soon. '
               'Hello, world! This is a test of my new, totally awesome system for using Pygame\'s font module '
               'to draw text. This will be a needed feature soon.', left=50, bottom=800, color=(210, 200, 150),
               font='Times', lineSpacing=24, spacing=5,  isBold=False, isItalic=False, maxRight=1000)
text4 = Text("`1234567890-=qwertyuop[]asdfghjkl;zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{} "
             "|ASDFGHJKL:\"ZXCVBNM<>?`™£¢∞§¶•ªº–≠œ∑´®†¥¨ˆøπ“‘«åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥µ")
testDisplay = Display(50, 1340, 850, 800, [text1, text2, text3, text4])
testDisplay.draw()
pygame.display.flip()
time.sleep(5)


def myPrint(msg, color: tuple[int, int, int]):
    testDisplay.texts = [Text(msg, color=color, left=testDisplay.left + 6, bottom=testDisplay.bottom - 6,
                              bottomShown=testDisplay.bottom - 6, maxRight=testDisplay.right - 6)] + testDisplay.texts


myPrint("Hi, world.", (200, 190, 255))

while True:
    actions = [i.key for i in pygame.event.get() if i.type == pygame.KEYDOWN]

    if pygame.K_c in actions:
        break

    if pygame.K_s in actions:
        testDisplay.scrollModifier -= 10

    if pygame.K_w in actions:
        testDisplay.scrollModifier += 10

    if pygame.K_a in actions:
        testDisplay.shift(-10, 0)

    if pygame.K_d in actions:
        testDisplay.shift(10, 0)

    display.fill((0, 0, 0))
    testDisplay.draw()
    pygame.display.flip()
    