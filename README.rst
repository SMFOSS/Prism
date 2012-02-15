=======
 Prism
=======

"NOVUS ORDO SECLORUM" 

A simple meta framework for webapps and services atop the `pyramid`
framework.


Pieces Parts
============

Pluggable configurator
----------------------

Prism provides a context manager based configurator (example taken
from `Bambino`)::

 from prism import configurator

 def main(global_config, settings):
     this = 'Bambino'
     with prism.configurator(appname=this,
                             global_config=global_config,
                             settings=settings) as config:
         config.add_translation_dirs('locale/')
         config.scan('bambino.views')
     return config.wsgiapp


The configurator scans the settings for the following keys::

 prism.root_class = prism.resource.App.factory
 prism.request = prism.request.Request.factory
 prism.stack = 
   prism.plugins.boilerplate
   bambino.plugins.appenv
   bambino.plugins.socketio

`prism.root_class`:

   A specification for a callable for creating an application root
   object and/or the root factory. This callable accepts the
   configurator as it's only argument and returns either a callable or
   an object w/ an attr 'root_factory' that will be registered as the
   context root factory.

`prism.request`

   A specification that will return a callable that takes the
   configurator as an argument and returns an object that may be
   registered as a request factory.

`prism.stack`

  A list of `plugins`: modules that provide at least a `includeme`
  callable and optionally callable "hooks".

  - modify_settings: configurator, settings
  - modify_resource_tree: configurator, app_root
  - after_user_config: configurator


Configuration execution
~~~~~~~~~~~~~~~~~~~~~~~

0. Pyramid `Configurator` initialized
1a. modify_settings hook foreach plugin
1b. if prism.root_class: modify_resource_tree hook foreach plugin
2. include foreach plugin
3. code in with block
4. after_user_config hook foreach plugin


App and BaseResource
--------------------

Some generic base classes and interfaces for use with the prism
configurator.  These are intended for applications that will build a
traversal tree at initial time (and extend it depending on request
behavior).  This useful if one wants to implement a polyglot
persistence strategy or simple stateless apps where it does not make
sense to hit a cache or persistence layer to render basic traversal
structure.

