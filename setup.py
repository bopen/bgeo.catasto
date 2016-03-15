from setuptools import setup, find_packages

version = '0.3.1'

setup(
    name='bgeo.catasto',
    version=version,
    description="Italian land registry utilities",
    long_description=open("README.rst").read(),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords='',
    author='Alessandro Amici',
    author_email='a.amici@bopen.eu',
    url='http://github.com/bopen/bgeo.catasto',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bgeo'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'future',
        'click',
        'GDAL',
        'SQLAlchemy',
    ],
    entry_points="""
        [console_scripts]
        cxf2ogr = bgeo.catasto.apps:main_cxf
    """,
)
