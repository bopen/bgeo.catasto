# -*- coding: utf-8 -*-

# python 2 support via python-future
from __future__ import absolute_import, division, print_function
# NOTE: do not import 'str' from builtins

import click

from bgeo.catasto import cxf
from bgeo.catasto import ogr


@click.command()
@click.argument('source')
@click.option('-d', '--destination', help="destination datasource name")
@click.option('-f', '--format-name', default='ESRI Shapefile',
              help="output file format name, see OGR docs for possible values")
@click.option('-P', '--point-borders', is_flag=True,
              help="add a duplicate BORDI layer with point features (useful for labeling)")
def main_cxf(source, destination, format_name='ESRI Shapefile', point_borders=False):
    source = str(source.partition('.CXF')[0])
    foglio = cxf.parse_foglio(source)
    if destination is None:
        destination = source
    ogr.write_foglio(foglio, destination, point_borders=point_borders, format_name=str(format_name))
