bgeo.catasto is a library for parsing and translating the proprietary data formats of
official Italian land registry data as published by the "Agenzia del Territorio"
into more standard GIS formats, like ESRI shapefiles.
It currently support CXF/SUP map files.

Installation
============

Dependencies:

- GDAL/OGR

Install dependencies on Ubuntu::

    $ sudo apt-get install -y libgdal-dev

Install the latest version from the Python Package Index::

    $ pip install bgeo.catasto

Translate the K550_000500.CXF/.SUP files to shapefiles::

    $ ls
    K550_000500.CXF	K550_000500.SUP
    $ cxf2ogr K550_000500.CXF
    [...]
    $ ls K550_000500
    K550_000500_BORDI.dbf		K550_000500_FIDUCIALI.prj	K550_000500_LINEE.shp		K550_000500_SIMBOLI.shx
    K550_000500_BORDI.prj		K550_000500_FIDUCIALI.shp	K550_000500_LINEE.shx		K550_000500_TESTI.dbf
    K550_000500_BORDI.shp		K550_000500_FIDUCIALI.shx	K550_000500_SIMBOLI.dbf		K550_000500_TESTI.prj
    K550_000500_BORDI.shx		K550_000500_LINEE.dbf		K550_000500_SIMBOLI.prj		K550_000500_TESTI.shp
    K550_000500_FIDUCIALI.dbf	K550_000500_LINEE.prj		K550_000500_SIMBOLI.shp		K550_000500_TESTI.shx

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
