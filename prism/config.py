from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.util import DottedNameResolver
import logging
import re


logger = logging.getLogger(__name__)


class prism(Configurator):
    """
    A context manager for configuring a pyramid webapp w/ plugins
    """
    comment_re=re.compile(r'^\s*(?P<spec>[a-zA-Z0-9_\.]+)\s*(?P<comment>#.*)?$')
    resolve = staticmethod(DottedNameResolver(None).maybe_resolve)
    stack_key = 'prism.stack'
    rf_kw = 'prism_root_factory'
    req_kw = 'prism_request_factory'

    def __init__(self, *args, **kw):
        self.settings = kw['settings']
        self.plugin_spec = self.settings[self.stack_key]
        self.app_factory = kw.pop(self.rf_kw, None)
        self.req_factory = kw.pop(self.req_kw, None)
        self.args = args
        self.kw = kw

    def specs_from_str(cls, string):
        return (cls.cleaner(p) for p in string.split('\n') if p.strip())

    @staticmethod
    def cleaner(string, regex=comment_re, key='spec'):
        string = string.strip()
        if string.startswith('#'):
            return None
        match = regex.match(string)
        if match:
            return match.groupdict()[key].strip()

        raise PluginSpecMalformed("<%s> is a malformed string" %string)

    @reify
    def loaded_plugins(self):
        return list(self.load(self.parsed_plugins))

    @reify
    def parsed_plugin(self):
        return list(self.specs_from_str(self.plugin_spec))

    def __enter__(self):
        if not self.app_factory is None:
            self.app_root = self.app_factory(self.settings)
            self.modify_resources(self.app_root, self.loaded_plugins, self.settings)
            self.kw['root_factory'] = self.app_root.root_factory
            
        if not self.req_factory is None:
            self.kw['request_factory'] = self.req_factory(self.plugins, self.settings)

        super(self, prism).__init__(*self.args, **self.kw)

    def __exit__(self, *args, **kw):
        # add error handling
        self.include_all_plugins()

    @property
    def wsgiapp(self):
        return self.make_wsgi_app()

    def include_all_plugins(self):
        return len(self.include(plugin) for plugin in self.parsed_plugins)

    @staticmethod
    def modify_resources(app, plugins, settings):
        for plugin in plugins:
            mod = getattr(plugin, 'modify_resources', None)
            if mod is not None:
                mod(settings, app)

    @classmethod
    def load(cls, plugins):
        """
        if a string, assume following format::

        >>> plugins = '''blah.plugin
            my.plugin  # I tell you what this is
            some.pkg
            # a comment
            '''

        """
        if isinstance(plugins, basestring):
            plugins = (x for x in cls.specs_from_str(plugins) if x)

        for plugin in plugins:
            try:
                yield cls.resolve(plugin)
            except ImportError, e:
                yield PluginNotFoundError('%s not importable: %s' %(plugin, e))
            except Exception, e:
                logger.error(e)
            yield e


class PluginSpecMalformed(ValueError):
    """
    A string to specify a plugin is malformed
    """
    
class PluginNotFoundError(ImportError):
    """
    A plugin is not found by the resolve
    """
