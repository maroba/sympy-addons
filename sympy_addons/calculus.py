from sympy import diff, Matrix, Add


def gradient(f, *coords):
    return Matrix([
        diff(f, c) for c in coords
    ])


def divergence(f, *coords):
    terms = [diff(f[i], c) for i, c in enumerate(coords)]
    return Add(*terms)


def curl(f, *xyz):
    if len(xyz) != 3:
        raise ValueError('curl can operate only in 3D.')
    return Matrix([
        diff(f[2], xyz[1]) - diff(f[1], xyz[2]),
        diff(f[0], xyz[2]) - diff(f[2], xyz[0]),
        diff(f[1], xyz[0]) - diff(f[0], xyz[1])
    ])
