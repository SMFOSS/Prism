from pyramid_jinja2 import renderer_factory


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_renderer('.html', renderer_factory)
