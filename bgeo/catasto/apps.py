
from optparse import OptionParser
from sys import argv


def main_cxf(args=argv[1:]):
    from bgeo.catasto.cxf import parse_foglio
    from bgeo.catasto.ogr import write_foglio

    parser = OptionParser()
    parser.add_option("-d", "--destination", 
        help="destination datasource name")
    parser.add_option("-f", "--format-name", default='ESRI Shapefile',
        help="output file format name, see OGR docs for possible values")
    parser.add_option("-P", "--point-borders", default=False, action="store_true",
        help="add a duplicate BORDI layer with point features (useful for labeling)")
    (keys, args) = parser.parse_args(args=args)
    assert len(args) == 1

    if args[0].endswith('.CXF'):
        args[0] = args[0][:-4]

    foglio = parse_foglio(args[0])
    if keys.destination is not None:
        destination = keys.destination
    else:
        destination = args[0]
    write_foglio(foglio, destination, point_borders=keys.point_borders,
        format_name=keys.format_name)


def main_ter(args=argv[1:]):
    from bgeo.catasto.ter import parse_censuario

    parser = OptionParser()
    parser.add_option("-d", "--destination", 
        help="destination datasource name")
    parser.add_option("-f", "--format-name", default='ESRI Shapefile',
        help="output file format name, see OGR docs for possible values")
    (keys, args) = parser.parse_args(args=args)
    assert len(args) == 1

    foglio = parse_censuario(args[0])
    if keys.destination is not None:
        destination = keys.destination
    else:
        destination = args[0]


if __name__ == '__main__':
    main_cxf()
