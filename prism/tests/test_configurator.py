from mock import patch, Mock
from nose.tools import raises
from prism.resource import App
from pyramid.view import view_config
from pyramid.interfaces import IRootFactory
import unittest


class TestPluginLoader(unittest.TestCase):

    def makeone(self):
        from prism import config; reload(config)
        plugin_text = """
        prism.plugins.boilerplate
        bambino.notexist
        # this one is fancy
        prism.plugins.fancy # builds the resource tree for appenvs
        """
        return config.configurator.load(plugin_text)
    
    def test_plugin_loader(self):
        from prism.plugins import boilerplate
        plugs = self.makeone()
        assert next(plugs) is boilerplate
        
    def test_notfound_plugin(self):
        _, exc, _ = self.makeone()
        from prism import config
        assert isinstance(exc, config.PluginNotFoundError)

    def test_unexpected_plugin(self):
        error = NotImplementedError('Surprise!!!!')
        with patch('pyramid.util.DottedNameResolver.maybe_resolve',
                   Mock(side_effect=error)):
            _, exc, _ = self.makeone()
        assert exc is error

    def test_commented_plugin(self):
        plugs = list(self.makeone())
        from prism.plugins import fancy
        assert plugs[-1] == fancy

    def test_cleaner(self):
        from prism import config
        assert config.configurator.cleaner('  hello #a comment\n') == 'hello'

    @raises(ValueError)
    def test_cleaner_error(self):
        from prism import config
        config.configurator.cleaner('???')

    @raises(ValueError)
    def test_cleaner_error_empty_string(self):
        from prism import config
        config.configurator.cleaner('')        



class CallableRoot(App):
    root_factory = None
    def __call__(self, req):
        return self

    def __repr__(self):
        return super(object, self).__repr__()


class TestConfigurator(unittest.TestCase):
    def_settings = {'prism.root_class':'prism.resource.App.factory',
                    'prism.request': 'prism.request.Request.factory',
                    'prism.stack':'prism.tests.pluggo'}

    def_gc = dict(here=__file__,
                  __file__=__file__)
              
    def makeone(self, name='test', settings=def_settings, gc=def_gc, **kw):
        from prism import config; reload(config)        
        with config.configurator(settings, appname='test', global_config=gc, **kw) as conf:
            conf.scan('prism.tests.test_configurator')
        return conf

    def test_application_of_hooks(self):
        conf = self.makeone()
        assert 'pluggo.added' in conf.settings
        assert hasattr(conf.app_root, 'pluggo_mod')
        assert hasattr(conf, 'after_user_config')
        assert hasattr(conf.registry, 'pluggo_included')

    def test_wsgiapp_creation(self):
        conf = self.makeone()
        assert conf.wsgiapp

    def test_user_deffed_rootfactory(self):
        rf = lambda req: App()
        conf = self.makeone(root_factory=rf)
        qrf = conf.registry.queryUtility(IRootFactory)
        assert qrf is rf, qrf

    def test_callable_rf(self):
        settings = self.def_settings.copy()
        settings['prism.root_class'] = 'prism.tests.test_configurator.CallableRoot'        
        conf = self.makeone(settings=settings)
        qrf = conf.registry.queryUtility(IRootFactory)
        assert isinstance(qrf, CallableRoot), qrf



@view_config(context='prism.interfaces.IApp')
def view(context, request):
    return "HELLO"


