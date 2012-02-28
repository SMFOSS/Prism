from pyramid_jinja2 import renderer_factory
from pyramid_jinja2 import parse_filters


def includeme(config):
    config.add_renderer('.html', renderer_factory)
    tmplt_dirs = config.settings.get('jinja2.directories')
    if tmplt_dirs:
        config.add_jinja2_search_path(tmplt_dirs)
    filters = config.settings.get('jinja2.filters')
    if filters:
        filters = parse_filters(filters)
        environment = config.get_jinja2_environment()
        environment.filters.update(filters)
