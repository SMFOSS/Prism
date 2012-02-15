from mock import patch, Mock
from nose.tools import raises
import unittest


class TestPluginLoader(unittest.TestCase):

    def makeone(self):
        from prism import config; reload(config)
        plugin_text = """
        prism.plugins.boilerplate
        bambino.notexist
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
