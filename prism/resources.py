from pyramid.url import resource_url
import threading
import os


class BaseResource(dict):
    """
    Base class for resources
    """
    resource_url = staticmethod(resource_url)
    
    def __init__(self, parent=None, name=None, **kwargs):
        self.__parent__ = parent
        self.__name__ = name
        super(BaseResource, self).__init__(**kwargs)

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
        resource = parent[name] = cls(name, parent, *args, **kwargs)
        return resource



class App(BaseResource):
    """
    Global traversal tree base
    """
    __name__ = ''
    __parent__ = None
    
    root = None 
    thread = threading.local()
    pid = os.getpid()

    def __init__(self, **kwargs):
        super(BaseResource, self).__init__(**kwargs)

    @classmethod
    def set_root(cls, root):
        cls.root = root

    @classmethod
    def root_factory(cls, request):
        cls.thread.request = request
        return cls.root

    @classmethod
    def factory(cls, settings, **kw):
        app = cls(**kw)
        cls.set_root(app)
        return app


root_factory = App.root_factory


