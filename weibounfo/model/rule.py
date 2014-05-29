# coding=utf-8


class Rule(object):
    def __init__(self, *args):
        self.checkers = args

    def test(self, obj):
        for c in self.checkers:
            if not c.check(obj):
                return False

        return True


class Checker(object):
    def __init__(self):
        pass

    def check(self, obj):
        return True


class Ops(object):
    def __init__(self, *args):
        self.checkers = args

    def check(self, obj):
        return True


class All(Ops):
    def check(self, obj):
        return all(c.check(obj) for c in self.checkers)


class Any(Ops):
    def check(self, obj):
        return any(c.check(obj) for c in self.checkers)


class Not(Ops):
    def check(self, obj):
        return not all(c.check(obj) for c in self.checkers)
