"""
A test plugin
"""

def modify_settings(config, settings):
    settings['pluggo.added'] = True
    config.modified_settings = True


def modify_resource_tree(config, app_root):
    app_root.pluggo_mod = True


def after_user_config(config):
    config.after_user_config = True


def includeme(config):
    config.registry.pluggo_included = True
