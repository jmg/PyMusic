try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False

from numpy import array, tan, pi

from visual.fractals.lindenmayer import FractalGen


class Pencil:

    COLOR = (0, 255, 255)

    LEN = 3

    offset = array([LEN, 0])
    pos = array([50, 900])
    angle = 90

    def __init__(self, screen):
        self.screen = screen

    def turn_left(self):
        if tuple(self.offset) == (self.LEN, 0):
            self.offset = array([0, self.LEN])
        elif tuple(self.offset) == (0, self.LEN):
            self.offset = array([-self.LEN, 0])
        elif tuple(self.offset) == (-self.LEN, 0):
            self.offset = array([0, -self.LEN])
        elif tuple(self.offset) == (0, -self.LEN):
            self.offset = array([self.LEN, 0])

    def turn_right(self):
        if tuple(self.offset) == (self.LEN, 0):
            self.offset = array([0, -self.LEN])
        elif tuple(self.offset) == (0, -self.LEN):
            self.offset = array([-self.LEN, 0])
        elif tuple(self.offset) == (-self.LEN, 0):
            self.offset = array([0, self.LEN])
        elif tuple(self.offset) == (0, self.LEN):
            self.offset = array([self.LEN, 0])

    def turn_left_with_angle(self, angle):
        self.angle += angle
        self._turn_left_with_angle()

    def _turn_left_with_angle(self):
        if (0 <= self.angle <= 45) or (315 < self.angle <= 360):
            x = round(tan(pi / 180 * self.angle), 2) * self.LEN
            y = self.LEN
            self.offset = array([x, y])
        elif 45 < self.angle <= 135:
            x = self.LEN
            y = round(tan(pi / 180 * 90 - pi / 180 * self.angle), 2) * self.LEN
            self.offset = array([x, y])
        elif 135 < self.angle <= 225:
            angle = 180 - self.angle
            x = round(tan(pi / 180 * angle), 2) * self.LEN
            y = -self.LEN
            self.offset = array([x, y])
        elif 225 < self.angle <= 315:
            angle = 180 - self.angle
            x = -self.LEN
            y = round(tan(pi / 180 * 90 - pi / 180 * angle), 2) * self.LEN
            self.offset = array([x, y])
        elif self.angle > 360:
            self.angle -= 360
            self._turn_left_with_angle()
        elif self.angle < 0:
            self.angle += 360
            self._turn_left_with_angle()

    def draw(self):
        if not _PYGAME_AVAILABLE:
            return
        pygame.draw.aaline(
            self.screen, self.COLOR,
            tuple(self.pos), tuple(self.pos + self.offset),
        )
        self.pos = self.pos + self.offset


if __name__ == "__main__":
    g = FractalGen()
    s = ""
    for _ in range(8):
        s = next(g)

    print(s)
