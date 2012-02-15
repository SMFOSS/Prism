from pyramid.decorator import reify
from pyramid.request import Request as Base


class Request(Base):
    @reify
    def settings(self):
        return self.registry.settings

    @reify
    def plugin(self):
        """
        returns plugin specific bits
        """
        pass 

    @classmethod
    def factory(cls, config):
        return cls
