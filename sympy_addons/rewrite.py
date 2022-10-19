import inspect


class RewriteManager:
    """Handles custom rewriting rules."""

    def __init__(self, obj):
        self.owner = obj
        self._eval_rewrite_original = obj._eval_rewrite
        self._rewrite_original = obj.rewrite
        self.existing_rules = {}
        self.custom_rules = {}

        manager = self

        def wrapped_rewrite(self, *args, **kwargs):
            rule = args[-1]
            func = self.rewrite_manager.get_rule_function(rule)
            if func:
                return func(*self.args, **kwargs)
            return manager._rewrite_original(self, *args, **kwargs)

        obj.rewrite = wrapped_rewrite

    def get_rule_function(self, rule):
        return self.custom_rules.get(rule)

    def add_rule(self, tag, rule_callable):
        self.custom_rules[tag] = rule_callable


def show_rewrite_rules(obj):
    """Prints all standard rewrite rules for a given object to stdout."""

    rules = {}

    method_name_head = '_eval_rewrite_as_'
    method_names = list(filter(lambda key: key.startswith(method_name_head), dir(obj)))

    for name in method_names:
        rule = name[len(method_name_head):]
        method = getattr(obj, name)
        code, _ = inspect.getsourcelines(method)
        rules[rule] = code

    for rule, code in rules.items():
        print('Rule: "{}"'.format(rule))
        for line in code:
            print(line, end='')


def customize_rewrite(cls):
    """Activate customization of given function or class."""
    cls.rewrite_manager = RewriteManager(cls)
