Introduction
============

bgeo.catasto is a library for parsing and translating official land registry data published by
the "Agenzia del Territorio" into more standard GIS formats.

It currently support CXF/SUP map files.

Installation
============

Dependencies:

- GDAL/OGR

To install dependencies on Ubuntu use::

    sudo apt-get install -y libgdal-dev

To install the package from the Python Package Index::

    pip install bgeo.catasto

Development
===========

Setup the development environment::

    git clone https://github.com/bopen/bgeo.catasto.git
    cd bgeo.catasto
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -e .

Test with::

    py.test
