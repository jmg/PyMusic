"""
    Un generador de terminos para la generacion de la curva de Koch
    a partir de un sistema de linden-mayer
"""
import re

def apply_rule(string, rules):

    rc = re.compile('|'.join(map(re.escape, rules)))
    def translate(match):
        return rules[match.group(0)]
    return rc.sub(translate, string)


def Gen(S, rules):
    while True:
        yield rules(S)
        S = rules(S)

def kochRule(s):
    rules = {'F' : 'F+F-F-F+F'}
    return apply_rule(s, rules)

def dragonRule(s):
    rules = {'X': 'X+YF', 'Y' : 'FX-Y'}
    return apply_rule(s, rules)

def sierpinskiRule(s):
    rules = {'A': 'B-A-B', 'B' : 'A+B+A'}
    return apply_rule(s, rules)


def FractalGen():
    return Gen('A', sierpinskiRule)



if __name__ == '__main__':
    g = Gen('A', sierpinskiRule)
    for x in range(4):
        print g.next()
