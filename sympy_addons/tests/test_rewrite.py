from sympy import sin, cos, pi
from sympy.abc import x

from sympy_addons.rewrite import customize_rewrite


def test_api():
    # Allow customization for sin, but not for other objects
    customize_rewrite(sin)

    expr = sin(2*x)

    sin.rewrite_manager.add_rule('half-angle', lambda x: 2 * sin(x / 2) * cos(x / 2))
    actual = expr.rewrite('half-angle')

    # With the custom rule defined, we should be able to use in with rewrite
    assert actual == 2 * sin(x) * cos(x), 'Custom rewrite rule failed'

    # The default rewrite of sine should still work:
    assert expr.rewrite(cos) == cos(2*x - pi/2, evaluate=False), 'Default rules should still work, but do not.'

    # We have only set up custom rewrite for sine,
    # so cosine should behave the same way as before:
    expr = cos(2*x)
    actual = expr.rewrite('half-angle')
    assert actual == cos(2*x), 'cos should have no custom rewrite.'
