import pytest
from sympy import epath, sqrt, Pow, Atom, Integer, sin
from sympy.abc import x, y, z

from sympy_addons.query import get_epaths, get_epath, NotUniqueException, NotFoundException, Query


def test_get_paths():
    expr = (x - 1) ** 2 + (x + 2) ** 2 / (x - 1) ** 2
    paths = get_epaths(x - 1, expr)
    assert len(paths) == 2
    assert epath(paths[0], expr)[0] == x - 1
    assert epath(paths[1], expr)[0] == x - 1


def test_get_path():
    expr = (x - 1) ** 2 + (x + 2) ** 2 / (x - 1) ** 2

    path = get_epath(x + 2, expr)
    assert epath(path, expr)[0] == x + 2

    with pytest.raises(NotUniqueException):
        get_epath(x - 1, expr)

    with pytest.raises(NotFoundException):
        get_epath(x + 1, expr)


def test_query_run():
    expr = (x - 1) ** 2 + ((x + 2) ** 2 + (x - 4) ** 3 + sin(z)) / sqrt((x - 1) ** 2 + (x + 3) ** 2)

    # Query by exact type
    query = Query(type=Pow)
    result = query.run(expr)
    assert len(result) == 6
    assert 1 / sqrt((x - 1) ** 2 + (x + 3) ** 2) in result

    # Query by base type
    query = Query(isinstance=Atom)
    result = query.run(expr)
    for item in result:
        assert isinstance(item, Atom)

    # Query by exact match
    query = Query(expr=(x - 1) ** 2)
    result = query.run(expr)
    assert len(result) == 2

    # Query by exact args
    query = Query(args=(x, Integer(2)))
    result = query.run(expr)
    assert len(result) == 1
    assert result.first() == x + 2

    # Order of args in query should not matter
    query = Query(args=(Integer(2), x))
    result = query.run(expr)
    assert len(result) == 1
    assert result.first() == x + 2

    # Query by partial args
    query = Query(args__contains=(-1,))
    result = query.run(expr)
    assert len(result) == 2
    assert result.first() == x - 1
    assert result.last() == x - 1

    # Query by custom test
    query = Query(test=lambda e: (not e.is_Atom) and len(e.args) == 3)
    result = query.run(expr)
    assert len(result) == 1
    assert result.first() == (x + 2) ** 2 + (x - 4) ** 3 + sin(z)


def test_concatenate_queries_with_or():
    expr = (x - 1) ** 2 + (x + 2) ** 2 / sqrt((x - 1) ** 2 + (x + 3) ** 2)

    query_1 = Query(expr=x - 1)
    query_2 = Query(expr=x + 2)

    result = (query_1 | query_2).run(expr)
    assert len(result) == 3
    assert x - 1 in result
    assert x + 2 in result


def test_filter_query_results():
    expr = (x - 1) ** 2 + (x + 2) ** 2 / sqrt((x - 1) ** 2 + (x + 3) ** 2)

    query_1 = Query(args__contains=(x,))
    result = query_1.run(expr)

    assert len(result) > 1
    for res in result:
        assert x in res.args

    query_2 = Query(args__contains=(x, 2))
    result = result.filter(query_2)

    assert len(result) == 1
    assert result.first() == x + 2

    query_3 = Query(args__contains=(y,))
    result = query_1.run(expr).filter(query_2).filter(query_3)
    assert len(result) == 0

    # Check if one can iterate over empty result set; shouldn't raise exception
    for _ in result:
        pass
