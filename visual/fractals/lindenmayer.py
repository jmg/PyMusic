"""Term generator for Lindenmayer-system fractals (Koch, dragon, Sierpiński)."""

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
    return apply_rule(s, {'F': 'F+F-F-F+F'})


def dragonRule(s):
    return apply_rule(s, {'X': 'X+YF', 'Y': 'FX-Y'})


def sierpinskiRule(s):
    return apply_rule(s, {'A': 'B-A-B', 'B': 'A+B+A'})


def FractalGen():
    return Gen('A', sierpinskiRule)


if __name__ == '__main__':
    g = Gen('A', sierpinskiRule)
    for _ in range(4):
        print(next(g))
