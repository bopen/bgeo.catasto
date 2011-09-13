from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='bgeo.catasto',
      version=version,
      description="Italian land registry utilities",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
          [console_scripts]
          cxf2ogr = bgeo.catasto.apps:main_cxf
          ter2db = bgeo.catasto.apps:main_ter
      """,
      )
