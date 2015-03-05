from setuptools import setup, find_packages

version = '0.2'

setup(
    name='bgeo.catasto',
    version=version,
    description="Italian land registry utilities",
    long_description=open("README.txt").read(),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords='',
    author='Alessandro Amici',
    author_email='',
    url='http://github.com/alexamici/bgeo.catasto',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bgeo'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'GDAL',
        'SQLAlchemy',
    ],
    entry_points="""
        [console_scripts]
        cxf2ogr = bgeo.catasto.apps:main_cxf
        ter2db = bgeo.catasto.apps:main_ter
    """,
)
