from sympy import Matrix
from sympy.abc import x, y, z

from sympy_addons.calculus import gradient, divergence


def test_gradient():

    f = x**2 + y**2 + z**2

    grad = gradient(f, x, y, z)
    assert grad == Matrix([2*x, 2*y, 2*z])

    grad = gradient(f, x, y)
    assert grad == Matrix([2 * x, 2 * y])


def test_divergence():

    grad_f = Matrix([2*x, 2*y, 2*z])

    div = divergence(grad_f, x, y, z)
    assert div == 6
