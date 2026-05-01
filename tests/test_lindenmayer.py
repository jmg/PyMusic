"""Lindenmayer-system rule + generator tests."""

from visual.fractals.lindenmayer import (
    FractalGen,
    Gen,
    apply_rule,
    dragonRule,
    kochRule,
    sierpinskiRule,
)


def test_apply_rule_translates_each_match():
    assert apply_rule('AB', {'A': 'X', 'B': 'Y'}) == 'XY'


def test_apply_rule_leaves_unmatched_chars_untouched():
    assert apply_rule('A-B+C', {'A': 'AA', 'B': 'BB'}) == 'AA-BB+C'


def test_koch_one_step():
    assert kochRule('F') == 'F+F-F-F+F'


def test_dragon_one_step():
    assert dragonRule('X') == 'X+YF'
    assert dragonRule('Y') == 'FX-Y'


def test_sierpinski_one_step():
    assert sierpinskiRule('A') == 'B-A-B'
    assert sierpinskiRule('B') == 'A+B+A'


def test_gen_iterates_repeatedly():
    g = Gen('A', sierpinskiRule)
    s1 = next(g)
    s2 = next(g)
    s3 = next(g)
    assert s1 == 'B-A-B'
    assert s2 == sierpinskiRule(s1)
    assert s3 == sierpinskiRule(s2)
    # Each iteration grows the string roughly 3x for sierpinski.
    assert len(s2) > len(s1)
    assert len(s3) > len(s2)


def test_fractal_gen_factory_uses_sierpinski():
    g = FractalGen()
    first = next(g)
    assert first == 'B-A-B'
