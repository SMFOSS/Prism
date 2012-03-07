"""
utility functions, decorators, context_managers, and descriptors
"""
class regattr(object):
    attr = 'registry'
    def __init__(self, name, default=AttributeError):
        self.name = name
        self.default = default

    def __get__(self, obj, objtype=None):
        base = getattr(obj, self.attr)
        if self.default is AttributeError:
            return getattr(base, self.name)
        return getattr(base, self.name, self.default)

    def __set__(self, obj, val):
        base = getattr(obj, self.attr)
        setattr(base, self.name, val)
