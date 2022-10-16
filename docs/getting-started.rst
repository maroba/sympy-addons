Getting Started
===============

Installation
------------

`sympy-addons` can be installed using pip:

.. code-block::

    pip install --upgrade sympy-addons

Usage
-----

The Query API
:::::::::::::


The query API allows to select specific subexpressions within SymPy expressions.
The examples in this section use the following expression for performing queries:

.. math::
    \left(x - 1\right)^{2} + \frac{\left(x - 4\right)^{3} + \left(x + 2\right)^{2} + \sin{\left(z \right)}}{\sqrt{\left(x - 1\right)^{2} + \left(x + 3\right)^{2}}}

or in SymPy:

.. code-block:: ipython

    from sympy import *
    from sympy.abc import x, z
    expr = (x - 1) ** 2 + ((x + 2) ** 2 + (x - 4) ** 3 + sin(z)) / sqrt((x - 1) ** 2 + (x + 3) ** 2)

Querying for types
..................

To get all subexpression matching a given type, e.g. `Pow`:

.. code-block:: ipython

    from sympy_addons import Query

    # define the query:
    query = Query(type=Pow)

    # execute it on an expression:
    result = query.run(expr)

    # result is an instance of QueryResult. You can iterate over it:
    for item in result:
        print(item)

    # or get the result as a list:
    this_is_a_list_of_matching_expressions = result.all()

    # or just the first/last:
    first_matching_expr = result.first()
    last_matching_expr = result.last()


Querying for inherited types
............................

To find all subexpressions that are instances of, say, `Atom` and all
classes inheriting from `Atom`, use the `isinstance` keyword:

.. code-block:: ipython

    query = Query(isinstance=Atom)


Querying for arguments
......................

Non-atomic types in SymPy have an `args` attribute. You can query for
subexpression which have exactly the `args` that you look for (order does not matter).
For example,

.. code-block::ipython

    result = Query(args=(x, 1)).run(expr)

will return all subexpressions with `args==(x, 1)` or `args==(1, x)`.

If you don't want to specify all `args`, use `args__contains` instead:

.. code-block::ipython

    result = Query(args__contains=(x,)).run(expr)

will return all subexpression with `args` attribute containing `x`.

Custom tests
............

You can define your own predicates to query for. For instance, to
query for subexpressions with exactly three arguments, you could write

.. code-block::ipython
    query = Query(test=lambd e: (not e.is_Atom) and len(e.args) == 3)


Chaining queries
................

Each query is defined as one predicate. But you can concatenate queries
to combine them logically.

For a logical OR, use the `|` operator:

.. code-block::ipython

    query_1 = ...
    query_2 = ...
    result = (query_1 | query_2).run(expr)

For an AND operation, use the `filter` method:

.. code-block::ipython

    query_1 = ...
    query_2 = ...
    result = query_1.run(expr).filter(query_2)


Getting `EPaths`
----------------

The `epath` function in SymPy allows to work directly on subexpressions. As input, it needs
the path to the subexpression, which is often cumbersome to get. The `get_paths` and `get_path`
facilitate getting those paths.

For example,

.. code-block::ipython

    from sympy_addons import get_epaths, get_epath

    paths = get_epaths((x-1)**2, expr)

returns

.. code-block::

    ['/[0]', '/[1]/[0]/[0]/[0]']

To only expand the :math:`(x-1)^2` under the square root, we would need the second path:

.. code-block::ipython

    epath(paths[1], expr, expand)


The `get_path` function works just as the `get_paths` function, but it will raise
an exception if the expression is not found or not unique.
