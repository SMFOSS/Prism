from pyramid import testing
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

    def test_suburls(self):
        request = testing.DummyRequest()
        from prism.resource import BaseResource as BR
        base = self.makeone(name='') # signal it's a root
        sub1 = BR.add_resource_to_tree(base, 'sub1')
        BR.add_resource_to_tree(base, 'sub2')
        output = list(sorted((url, obj) for obj, url in base.suburls(request)))
        assert len(output) == 2
        assert output[0][0] == 'http://example.com/sub1', output[0][0]
        assert output[0][1] is sub1


class TestApp(unittest.TestCase):
    
    def makeone(self, **kw):
        from prism.resource import App
        return App.factory({})

    def test_factory(self):
        app = self.makeone()
        from prism.resource import App
        assert App.root is app

    def test_root_factory(self):
        app = self.makeone()
        request = testing.DummyRequest()
        ret = app.root_factory(request)
        assert app is ret
        assert app.thread.request is request


class TestSuperInit(unittest.TestCase):
    def makeone(self):
        from prism.resource import superinit
        class Sup(dict):
            def __init__(self, s1, **kw):
                with superinit(self, **kw):
                    self.s1 = s1
        return Sup

    def test_superinit(self):
        cls = self.makeone()
        obj = cls(1, what=2)
        assert 'what' in obj
        assert obj.s1 == 1
