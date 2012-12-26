Introduction
============

bgeo.catasto is a library for parsing and translating
official land registry data published by the "Agenzia
del Territorio" into more standard GIS formats.

It currently support CXF/SUP map files and FAB/TER
censo data.

Dependencies
============

 * Python
 * GDAL/OGR + pyhton bindings
 * SQLalchemy + psycopg2 (for uploading censo data to a PostgeSQL db)

On Ubuntu use:

  $ sudo apt-get install -y python-gdal python-sqlalchemy python-psycopg2
