
from optparse import OptionParser
from os.path import basename
from sys import argv

from bgeo.catasto.cxf import parse_foglio
from bgeo.catasto.ogr import write_foglio

def main(args=argv[1:]):
    parser = OptionParser()
    parser.add_option("-d", "--destination", 
        help="destination datasource name")
    parser.add_option("-f", "--format-name", default='ESRI Shapefile',
        help="output file format name, see OGR docs for possible values")
    (keys, args) = parser.parse_args(args=args)
    assert len(args) == 1

    foglio = parse_foglio(args[0])
    if keys.destination is not None:
        destination = keys.destination
    else:
        destination = args[0]
    write_foglio(foglio, destination)

if __name__ == '__main__':
    main()
