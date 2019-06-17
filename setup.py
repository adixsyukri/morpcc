from setuptools import setup, find_packages
import sys, os

version = '0.1.0a3'

setup(name='morpcc',
      version=version,
      description="Morp Control Center",
      long_description="""\
A meta CMS built on top of MorpFW""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='framework cms',
      author='Izhar Firdaus',
      author_email='kagesenshi.87@gmail.com',
      url='http://github.com/morpframework/morpcc',
      license='LGPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "morpfw==0.2.1",
          "more.chameleon",
          "more.static",
          "deform",
          "beaker"
      ],
      entry_points={
      })
