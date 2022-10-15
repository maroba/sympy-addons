from sympy import preorder_traversal


class Query:
    """A class for querying SymPy expression."""

    def __init__(self, **kwargs):

        self._validate_kwargs(kwargs)
        self.kwargs = kwargs

        self.tests = []

        if 'initial_tests' in kwargs:
            tests = kwargs['initial_tests']
            try:
                iter(tests)
                for t in tests:
                    if not callable(t):
                        raise ValueError
            except:
                raise ValueError('initial_tests must be an iterable of callables.')
            self.tests = tests
            return

        if 'type' in kwargs:
            self.tests.append(lambda e: type(e) == kwargs['type'])
        elif 'isinstance' in kwargs:
            # Pycharm reports an error here, but this is just a PyCharm bug.
            # See: https://stackoverflow.com/questions/56493140/parameterized-generics-cannot-be-used-with-class-or-instance-checks
            self.tests.append(lambda e: isinstance(e, kwargs['isinstance']))
        elif 'args' in kwargs:
            args = kwargs['args']
            if not isinstance(args, tuple) and not isinstance(args, list):
                args = tuple(args)
            def test_args(e):
                if e.is_Atom: # atoms have no args
                    return False
                return all(arg in e.args for arg in args) and len(args) == len(e.args)
            self.tests.append(test_args)
        elif 'args__contain' in kwargs:
            args = kwargs['args__contain']
            if not isinstance(args, tuple) and not isinstance(args, list):
                args = tuple(args)
            def test_args__contain(e):
                if e.is_Atom: # atoms have no args
                    return False
                return all(arg in e.args for arg in args)
            self.tests.append(test_args__contain)
        elif 'expr' in kwargs:
            self.tests.append(
                lambda e: e == kwargs['expr']
            )
        elif 'test' in kwargs:
            test = kwargs['test']
            if not callable(test):
                raise TypeError('{} is not callable.'.format(repr(test)))
            self.tests.append(test)
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
        assert type(other) == Query
        tests = self.tests + other.tests
        return Query(initial_tests=tests)

    def __repr__(self):
        return str(self.kwargs)

    def _validate_kwargs(self, kwargs):
        allowed_keywords = [
            'type',  # tests if type are exactly equal
            'isinstance',  # tests if type is same or child class
            'expr',  # tests if the subexpr exactly matches
            'args',  # tests if args exactly match
            'args__contain',  # tests if args contain all of the given tuple items
            'test',  # user-defined matching test
            'initial_tests',  # give initial set of test functions (for internal-use only)
        ]
        num_keywords_found = 0
        for key in kwargs:
            if not key in allowed_keywords:
                raise ValueError('Invalid keyword in Query constructor: %s' % key)
            num_keywords_found += 1
        if num_keywords_found == 0:
            raise ValueError('No query parameters defined.')
        if num_keywords_found > 1:
            raise ValueError('Only one query parameter may be set.')


class QueryResult:

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
