from .utils import regattr 
from pyramid.config import Configurator as Base
from pyramid.path import caller_package
from pyramid.util import DottedNameResolver
import logging
import re


logger = logging.getLogger(__name__)




class configurator(Base):
    """
    A context manager for configuring a pyramid webapp w/ plugins
    """
    comment_re=re.compile(r'^\s*(?P<spec>[a-zA-Z0-9_\.]+)\s*(?P<comment>#.*)?$')
    open_resolve = staticmethod(DottedNameResolver(None).maybe_resolve)
    stack_key = 'prism.stack'
    rf_kw = 'prism.root_class'
    req_kw = 'prism.request'

    root_factory_set = regattr('_root_factory_set', False)
    app_factory = regattr('app_factory')
    request_factory = regattr('request_factory')
    plugin_spec = regattr('plugin_spec')
    appname = regattr('appname')
    config_file = regattr('config_file')
    exec_dir = regattr('exec_dir')
    parsed_plugins = regattr('parsed_plugins')
    loaded_plugins = regattr('loaded_plugins')
    app_root = regattr('app_root')
    _settings = regattr('_prism_settings')

    def __init__(self, settings=None, appname=None, global_config=None, **base_kwargs):
        package = base_kwargs.get('package') or caller_package()
        base_kwargs['package'] = package
        super(configurator, self).__init__(settings=settings, **base_kwargs)
        if 'root_factory' in base_kwargs:
            self.root_factory_set = True
        if settings:
            settings = dict(settings)
            self._settings = settings.copy()
            base_kwargs['settings'] = settings

            self.app_factory = self.rf_kw in settings \
                               and self.open_resolve(settings[self.rf_kw]) 

            self.request_factory = self.req_kw in settings \
                                   and self.open_resolve(settings[self.req_kw]) 

            self.plugin_spec = settings.get(self.stack_key, None)
        
        if appname:
            self.appname = appname

        if global_config:
            self.config_file = global_config['__file__']
            self.exec_dir = global_config['here']        

    @property
    def settings(self):
        return self.registry.settings

    @property
    def this(self):
        return self.registry.appname

    def __enter__(self):
        self.parsed_plugins = list(self.specs_from_str(self.plugin_spec))
        self.loaded_plugins = list(self.load(self.parsed_plugins))
        self.apply_hook('modify_settings', self.registry.settings) # maybe use events
        if not self.app_factory in (False, None):
            self.app_root = self.app_factory(self)
            self.apply_hook('modify_resource_tree', self.app_root)
            if  self.root_factory_set is False:
                rf = getattr(self.app_root, 'root_factory', None)
                if rf is None:
                    if callable(self.app_root):
                        rf = self.app_root 

                if not rf is None:
                    self.set_root_factory(rf)
                    self.root_factory_set = True

        if not self.request_factory in (False, None):
            self.set_request_factory(self.request_factory(self))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # add error handling
        self.include_all_plugins()
        self.apply_hook('after_user_config') # maybe use events
        self.commit()

    @classmethod
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

    @property
    def wsgiapp(self):
        app = self.make_wsgi_app()
        app.__app_name__ = self.this
        return app

    def include_all_plugins(self):
        return len([self.include(plugin) for plugin in self.parsed_plugins])

    def apply_hook(self, hook_name, *args, **kw):
        for plugin in self.loaded_plugins:
            mod = getattr(plugin, hook_name, None)
            if mod is not None:
                if not mod is callable:
                    mod = self.open_resolve(mod)
                try:
                    mod(self, *args, **kw)
                    setattr(mod, "__%s__" %self.this, True)
                except Exception, e:
                    #@@ sensible catching and repackaging of traceback
                    logger.error("%s %s %s", hook_name, mod.__module__, e)
                    raise

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
                yield cls.open_resolve(plugin)
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
    A plugin is not found by the resolver
    """
