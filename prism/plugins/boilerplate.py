"""
A basic prism app boilerplate
"""
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from prism.request import Request


def before_config(config, settings, **kw):
    settings.setdefault('jinja2.i18n.domain', config.this)


def includeme(config):
    config.__boilerplate_loaded__ = True
    config.include('prism.plugins.jinja2')
    config.set_session_factory(UnencryptedCookieSessionFactoryConfig(config.this))
    config.add_static_view('static', 'static')
    config.set_request_factory(Request)
