from .interfaces import IApp
from .interfaces import IResource
from contextlib import contextmanager as cm
from pyramid.url import resource_url
from zope.interface import implementer
import os
import threading


@implementer(IResource)
class BaseResource(dict):
    """
    Base class for resources
    """
    resource_url = staticmethod(resource_url)
    
    def __init__(self, parent=None, name=None, **kwargs):
        super(BaseResource, self).__init__(**kwargs)
        self.__parent__ = parent
        self.__name__ = name

    @property
    def approot(self):
        return self.recurse_parent(self.root_class)
            
    def recurse_parent(self, klass, parent=None, origin=None):
        if parent is None:
            parent = self.__parent__
            if parent is None:
                origin = self
        else:
            origin = parent
            parent = parent.__parent__

        if parent is None:
            # we've reached end of the tree (though not necessarily a
            # class match)
            return origin
        
        if isinstance(parent, klass):
            return parent

        return self.recurse_parent(klass, parent)
    
    def suburls(self, request):
        for name in sorted(self):
            obj = self[name]
            url = self.resource_url(self, request, name)
            yield obj, url    

    @property
    def root_class(self):
        return App

    @classmethod
    def add_resource_to_tree(cls, parent, name, *args, **kwargs):
        resource = parent[name] = cls(parent, name,  *args, **kwargs)
        return resource


@implementer(IApp)
class App(BaseResource):
    """
    Global in-memory traversal tree base
    """
    __name__ = ''
    __parent__ = None
    
    root = None 
    thread = threading.local()
    pid = os.getpid()

    @classmethod
    def set_root(cls, root):
        cls.root = root

    @classmethod
    def root_factory(cls, request):
        cls.thread.request = request
        return cls.root

    @classmethod
    def factory(cls, config): #@@ do we really need config??
        app = cls()
        cls.set_root(app)
        return app


@cm
def superinit(obj, *args, **kw):
    try:
        yield
    finally:
        super(obj.__class__, obj).__init__(*args, **kw)


root_factory = App.root_factory


