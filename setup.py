from setuptools import find_packages
from setuptools import setup

version = '0.0'

requires = ['pyramid']

setup(name='Prism',
      version=version,
      description="A simple plugin system for pyramid",
      long_description=open('README.rst').read(),
      classifiers=[], 
      keywords='',
      author='',
      author_email='',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
