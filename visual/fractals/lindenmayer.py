"""
    Un generador de terminos para la generacion de la curva de Koch
    a partir de un sistema de linden-mayer
"""

def rule(s):
    return s.replace('F', 'F+F-F-F+F')

def gen(S='F'):
    while True:
        yield rule(S)
        S = rule(S)

if __name__ == '__main__':
    g = gen()
    for x in range(4):
        print g.next()

