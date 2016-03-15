
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
def main_cxf(source, destination, format_name, point_borders):
    source = source.partition('.CXF')[0]
    foglio = cxf.parse_foglio(source)
    if destination is None:
        destination = source
    ogr.write_foglio(foglio, destination, point_borders=point_borders, format_name=format_name)


# def main_censuario(args=argv[1:]):
#     from bgeo.catasto.censuario import parse_censuario
#     from bgeo.catasto.db import upload_censuario
#
#     parser = OptionParser()
#     parser.add_option("-d", "--dsn", default='postgresql:///', help="destination datasource name")
#     (keys, args) = parser.parse_args(args=args)
#     assert len(args) == 1
#
#     censuario = parse_censuario(args[0])
#     upload_censuario(keys.dsn, censuario)
