from sympy import preorder_traversal, latex


class Query:
    """A class for querying SymPy expression."""

    def __init__(self, **kwargs):
        """Public Constructor for Query instance.

        Parameters
        ----------
        kwargs : keyword arguments
            Specifies what query to perform.

            Keys (only ONE at a time is allowed):

                'type'
                    Value can be any type.
                    Returns all subexpressions with given type.

                'isinstance'
                    Value can be any type.
                    Returns all subexpressions with a type that is inheriting from given type.

                'expr'
                    Value can be any SymPy expression or symbol.
                    Returns all subexpressions exactly equal to given value.

                'args'
                    Value must be a tuple of SymPy objects.
                    Returns all subexpressions with args attribute matching the value.
                    The order of the value-tuple does not matter.

                'args__contains'
                    Value must be a tuple of SymPy objects.
                    Returns all subexpression with args attribute containing all of the objects
                    in the given value tuple.

                'test'
                    Value must be a callable, only argument is the expression to test, body is a
                    predicate on the expression to test.
                    Returns all subexpressions matching the given predicate.

        """

        self._validate_keywords(kwargs)
        self.kwargs = kwargs

        self.tests = []

        negate = kwargs.get('negate', False)

        if 'type' in kwargs:
            self.tests.append(IsType(kwargs['type'], negate))
        elif 'isinstance' in kwargs:
            self.tests.append(IsInstance(kwargs['isinstance'], negate))
        elif 'args' in kwargs:
            self.tests.append(ArgsEquals(kwargs['args'], negate))
        elif 'args__contains' in kwargs:
            self.tests.append(ArgsContains(kwargs['args__contains'], negate))
        elif 'expr' in kwargs:
            self.tests.append(ExprEquals(kwargs['expr'], negate))
        elif 'latex' in kwargs:
            self.tests.append(LatexEquals(kwargs['latex'], negate))
        elif 'latex__contains' in kwargs:
            self.tests.append(LatexContains(kwargs['latex__contains'], negate))
        elif 'test' in kwargs:
            self.tests.append(Predicate(kwargs['test'], negate))
        elif 'tests' in kwargs:
            tests = kwargs['tests']
            valid_tests = []
            try:
                iter(tests)
                for t in tests:
                    if not callable(t):
                        raise ValueError
                    if not isinstance(t, Predicate):
                        t = Predicate(t)
                    if negate:
                        t = t.negated()
                    valid_tests.append(t)
            except:
                raise ValueError('tests must be an iterable of callables.')
            self.tests = valid_tests
        else:
            raise AssertionError('This should not happen.')

    def run(self, expr):
        """Run the query on an expression."""
        result = QueryResult()
        for part in preorder_traversal(expr):
            if self.matches(part):
                result.extend([part])
        return result

    def matches(self, expr):
        for test in self.tests:
            if test(expr):
                return True
        return False

    def __or__(self, other):
        """Returns a query that matches is self-query matches OR other query matches."""
        assert type(other) == Query
        tests = self.tests + other.tests
        return Query(tests=tests)

    def __repr__(self):
        return repr(self.kwargs)

    def _validate_keywords(self, kwargs):
        allowed_unique_keywords = [
            'type',  # tests if type are exactly equal
            'isinstance',  # tests if type is same or child class
            'expr',  # tests if the subexpr exactly matches
            'args',  # tests if args exactly match
            'args__contains',  # tests if args contain all of the given tuple items
            'latex',  # tests is latex representation of subexpression matches
            'latex__contains',  # tests if latex representation of subexpression contains value
            'test',  # user-defined matching test
            'tests',  # give initial set of test functions
        ]
        allowed_other_keywords = [
            'negate'
        ]
        num_keywords_found = 0
        for key in kwargs:
            if key not in allowed_unique_keywords and key not in allowed_other_keywords:
                raise ValueError('Invalid keyword in Query constructor: %s' % key)
            if key in allowed_unique_keywords:
                num_keywords_found += 1
        if num_keywords_found == 0:
            raise ValueError('No query parameters defined.')
        if num_keywords_found > 1:
            raise ValueError('Only one query parameter may be set.')


class Predicate:

    def __init__(self, test, negate=False):
        if not callable(test):
            raise TypeError('Predicate argument must be callable!')
        self._negate = negate
        self._test = test

    def __call__(self, expr, *args, **kwargs):
        if self._negate:
            return not self._test(expr, *args, **kwargs)
        return self._test(expr, *args, **kwargs)

    def negated(self):
        return type(self)(
            lambda e, *args, **kwargs: not self._test(e, *args, **kwargs),
            negate=not self._negate
        )

    def __repr__(self):
        if self._negate:
            return 'not {}'.format(type(self).__name__)
        return type(self).__name__

class IsType(Predicate):

    def __init__(self, the_type, negate=False):
        super(IsType, self).__init__(lambda e: type(e) == the_type, negate)


class IsInstance(Predicate):

    def __init__(self, parent_type, negate=False):
        super(IsInstance, self).__init__(lambda e: isinstance(e, parent_type), negate)


class ExprEquals(Predicate):

    def __init__(self, expr, negate=False):
        super(ExprEquals, self).__init__(lambda e: e == expr, negate)


class ArgsEquals(Predicate):

    def __init__(self, args, negate=False):
        if not isinstance(args, tuple) and not isinstance(args, list):
            args = tuple(args)

        def test_args(e):
            if e.is_Atom:  # atoms have no args
                return False
            return all(arg in e.args for arg in args) and len(args) == len(e.args)

        super(ArgsEquals, self).__init__(test_args, negate)


class ArgsContains(Predicate):

    def __init__(self, some_args, negate=False):
        if not isinstance(some_args, tuple) and not isinstance(some_args, list):
            some_args = tuple(some_args)

        def test_args__contains(e):
            if e.is_Atom:  # atoms have no args
                return False
            return all(arg in e.args for arg in some_args)

        super(ArgsContains, self).__init__(test_args__contains, negate)


class LatexEquals(Predicate):

    def __init__(self, latex_str, negate=False):
        def test_latex(e):
            latex_repr = _searchable_latex_str(latex(e))
            return latex_repr == _searchable_latex_str(latex_str)

        super(LatexEquals, self).__init__(test_latex, negate)


class LatexContains(Predicate):

    def __init__(self, latex_str, negate=False):
        def test_latex_contains(e):
            latex_repr = _searchable_latex_str(latex(e))
            return _searchable_latex_str(latex_str) in latex_repr

        super(LatexContains, self).__init__(test_latex_contains, negate)


class QueryResult:

    # TODO: intersection and union of query results

    def __init__(self, expr_list=None):
        self._expr_list = expr_list or []
        self._counter = None

    def filter(self, query):
        result = QueryResult()
        for expr in self._expr_list:
            result.extend(query.run(expr).all())
        return result

    def first(self):
        return self._expr_list[0]

    def last(self):
        return self._expr_list[-1]

    def all(self):
        return self._expr_list

    def extend(self, expr_list):
        self._expr_list.extend(expr_list)

    def as_set(self):
        return set(self._expr_list)

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if self._counter == len(self._expr_list):
            raise StopIteration
        result = self._expr_list[self._counter]
        self._counter += 1
        return result

    def __len__(self):
        return len(self._expr_list)

    def __repr__(self):
        return '[' + ', '.join(repr(e) for e in self) + ']'


class QueryException(Exception):
    pass


class NotUniqueException(QueryException):
    pass


class NotFoundException(QueryException):
    pass


class Node:
    """
    A node in the expression tree.

    Wraps around the SymPy expression node and contains path information.
    Makes only sense in the context of expression and path queries, where
    we have a containing expression.
    """

    def __init__(self, parent, expr, path):
        self.expr = expr
        self.parent = parent
        self.children = []
        self.path = path or ''

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def __repr__(self):
        return repr(self.expr) + ' ({})'.format(self.path)


def make_expression_tree(expr):
    """Build the expression tree with path information.

    Parameters
    ----------
    expr : Basic
        The root expression for the expression tree to build.

    Returns
    -------
    out :   Node
        The root node of the expression tree.
    """

    def walk(node):
        if node.expr.is_Atom:
            return
        for idx, arg in enumerate(node.expr.args):
            child_path = node.path + '/[{}]'.format(idx)
            child_node = Node(node, arg, child_path)
            node.add_child(child_node)
            if not arg.is_Atom:
                walk(child_node)

    root = Node(None, expr, None)
    walk(root)
    return root


def walk_tree(root_node):
    """Returns a list of all nodes in the expression tree."""
    all_nodes = []

    def _walk(node):
        all_nodes.append(node)
        if node.children:
            for child in node.children:
                _walk(child)

    _walk(root_node)
    return all_nodes


def get_epaths(subexpr, containing_expr):
    """Get all epaths for a subexpression within a given expression.

    Parameters
    ----------
    subexpr : Basic
        The subexpression to get epaths for.
    containing_expr : Basic
        The containing expression.

    Returns
    -------
    out : list
        A list of epath-strings matching the subexpression.
    """
    tree = make_expression_tree(containing_expr)
    paths = []
    for node in walk_tree(tree):
        if node.expr == subexpr:
            paths.append(node.path)
    return paths


def get_epath(subexpr, containing_expr):
    """Get the unique epath for a subexpression within a given expression.

    Parameters
    ----------
    subexpr : Basic
        The subexpression to get epaths for.
    containing_expr : Basic
        The containing expression.

    Returns
    -------
    out : str
        The epath string for the matching subexpression.

    Raises
    ------
    NotUniqueException
        if the subexpression is not unique in the containing expression.
    NotFoundException
        if the subexpression is not found in the containing expression.

    """
    paths = get_epaths(subexpr, containing_expr)
    if len(paths) > 1:
        raise NotUniqueException
    if len(paths) == 0:
        raise NotFoundException
    return paths[0]


def _searchable_latex_str(latex_repr):
    return latex_repr.replace(' ', '').replace(r'\left', '').replace(r'\right', '')
