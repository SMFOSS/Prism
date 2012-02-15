import unittest

class TestBaseResource(unittest.TestCase):
    
    def makeone(self, **kw):
        from prism.resource import BaseResource
        return BaseResource(**kw)
        
    def test_init(self):
        br = self.makeone()
        assert br.__name__ is None
        assert br.__parent__ is None
        br = self.makeone(parent='dad', name='kid')
        assert br.__name__ == 'kid'
        assert br.__parent__ == 'dad'
        br = self.makeone(parent='dad', name='kid', blah=2, wizz=3)
        assert 'blah' in br and 'wizz' in br
        assert br.__name__ == 'kid'
        assert br.__parent__ == 'dad'

    def make_tree(self, parent, tree_spec):
        for name, subspec in tree_spec.items():
            resource = parent[name] = self.makeone(name=name, parent=parent)
            if subspec:
                parent[name].update(self.make_tree(resource, subspec))
        return parent

    def test_recurse_to_approot(self):
        from prism.resource import App
        app = self.make_tree(App(), dict(branch1={}, branch2=dict(leaf=dict())))
        assert app is app['branch1'].approot
        assert app is app['branch2']['leaf'].approot
        assert app is app.approot 
