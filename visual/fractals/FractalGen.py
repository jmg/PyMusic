import pygame
from lindenmayer import *
from numpy import *

pygame.init()

class Pencil(object):

    SIZE = (1000,1000)
    screen = pygame.display.set_mode(SIZE)

    COLOR = (0,255,255)

    LEN = 3

    offset = array([LEN ,0])
    pos = array([50,900])
    angle = 90

    def turn_left(self):
        if tuple(self.offset) == (self.LEN ,0):
            self.offset = array([0,self.LEN ])
        elif tuple(self.offset) == (0,self.LEN ):
            self.offset = array([-self.LEN ,0])
        elif tuple(self.offset) == (-self.LEN ,0):
            self.offset = array([0,-self.LEN ])
        elif tuple(self.offset) == (0,-self.LEN ):
            self.offset = array([self.LEN ,0])

    def turn_right(self):
        if tuple(self.offset) == (self.LEN ,0):
            self.offset = array([0,-self.LEN ])
        elif tuple(self.offset) == (0,-self.LEN ):
            self.offset = array([-self.LEN ,0])
        elif tuple(self.offset) == (-self.LEN ,0):
            self.offset = array([0,self.LEN ])
        elif tuple(self.offset) == (0,self.LEN ):
            self.offset = array([self.LEN ,0])

    def turn_left_with_angle(self, angle):
        self.angle += angle
        self._turn_left_with_angle()

    def _turn_left_with_angle(self):
        if (self.angle >= 0 and self.angle <= 45) or (self.angle > 315 and self.angle <= 360):
            x = round(tan(pi/180 * self.angle),2) * self.LEN
            y = self.LEN
            self.offset = array([x, y])
        elif self.angle > 45 and self.angle <= 135:
            x = self.LEN
            y = round(tan(pi/180 * 90 - pi/180 * self.angle),2) * self.LEN
            self.offset = array([x, y])
        elif self.angle > 135 and self.angle <= 225:
            angle = 180 - self.angle
            x = round(tan(pi/180 * angle),2) * self.LEN
            y = -self.LEN
            self.offset = array([x, y])
        elif self.angle > 225 and self.angle <= 315:
            angle = 180 - self.angle
            x = -self.LEN
            y = round(tan(pi/180 * 90 - pi/180 * angle),2) * self.LEN
            self.offset = array([x, y])
        elif self.angle > 360:
            self.angle = self.angle - 360
            self._turn_left_with_angle()
        elif self.angle < 0:
            self.angle = self.angle + 360
            self._turn_left_with_angle()

    def draw(self):
        pygame.draw.line(self.screen, self.COLOR, tuple(self.pos), tuple(self.pos + self.offset))
        pygame.display.flip()
        self.pos = self.pos + self.offset


g = FractalGen()
s = ""
for x in range(8):
    s = g.next()

print s
p = Pencil()

def drawer():
    for c in s:
        if c == 'F':
            p.draw()
        elif c == '-':
            p.turn_right()
        elif c == '+':
            p.turn_left()

def t():
    for c in s:
        if c == 'A' or c == 'B':
            p.draw()
        elif c == '+':
            p.turn_left_with_angle(60)
        elif c == '-':
            p.turn_left_with_angle(-60)

#drawer()
t()


