
import sys

from bgeo.catasto.cxf import do_main
from bgeo.catasto.ogr import foglio_to_shapefiles

def main():
    basepath = sys.argv[1]
    foglio = do_main(basepath)
    foglio_to_shapefiles(foglio, basepath)

if __name__ == '__main__':
    main()
