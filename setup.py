from setuptools import find_packages
from setuptools import setup

version = '0.0a1'

requires = ['pyramid', 
            'pyramid_jinja2']

setup(name='Prism',
      version=version,
      description="A simple plug driven framework atop pyramid",
      long_description=open('README.rst').read(),
      classifiers=[], 
      keywords='',
      author='',
      author_email='whit at surveymonkey.com',
      url='http://prism.github.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
