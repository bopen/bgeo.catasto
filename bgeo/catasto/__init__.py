
from os import mkdir
from os.path import join, basename as path_basename
import sys

from osgeo.osr import CoordinateTransformation, SpatialReference
from osgeo.ogr import GetDriverByName, wkbPoint, wkbPolygon, wkbLinearRing, Feature, Geometry, FieldDefn
from osgeo.ogr import OFTString, OFTInteger, OFTReal

local_cassini_soldener = SpatialReference()
# local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0.8 +y_0=-1.3 +ellps=intl +units=m +no_defs')
local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0 +y_0=0 +ellps=intl +units=m +no_defs')
gauss_boaga_ovest = SpatialReference()
gauss_boaga_ovest.ImportFromEPSG(3004)

trasformation = CoordinateTransformation(local_cassini_soldener, gauss_boaga_ovest)


def foglio_to_shapefiles(foglio, outpath):
    mkdir(outpath)

    f_comune = FieldDefn('comune', OFTString)
    f_comune.SetWidth(4)
    f_foglio = FieldDefn('foglio', OFTString)
    f_foglio.SetWidth(11)
    f_part = FieldDefn('part', OFTString)
    f_part.SetWidth(8)
    f_dimensione = FieldDefn('dimensione', OFTInteger)
    f_pos_x = FieldDefn('pos_x', OFTReal)
    f_pos_y = FieldDefn('pos_y', OFTReal)
    f_interno_x = FieldDefn('interno_x', OFTReal)
    f_interno_y = FieldDefn('interno_y', OFTReal)

    layers = {}
    for tipo_bordo in ['confini', 'strade', 'acque', 'edifici', 'particelle']:
        ds = GetDriverByName('ESRI Shapefile').CreateDataSource(join(outpath, tipo_bordo + '.shp'))
        layer = ds.CreateLayer(tipo_bordo, None, wkbPolygon)

        layer.CreateField(f_comune)
        layer.CreateField(f_foglio)
        layer.CreateField(f_part)
        layer.CreateField(f_dimensione)
        layer.CreateField(f_pos_x)
        layer.CreateField(f_pos_y)
        layer.CreateField(f_interno_x)
        layer.CreateField(f_interno_y)
        
        # NEVER EVER LOSE THE REFERENCE TO ds!
        layers[tipo_bordo] = (layer, ds)

    for bordo in foglio['oggetti']['BORDO']:
        poly = Geometry(wkbPolygon)
        tabisole = map(int, bordo['TABISOLE'])

        # contorno esterno
        vertici_contorno = int(bordo['NUMEROVERTICI']) - sum(tabisole)
        ring = Geometry(wkbLinearRing)
        for vertice in range(vertici_contorno):
            x, y = map(float, bordo['VERTICI'][vertice])
            if True:
                x, y = trasformation.TransformPoint(x, y)[:2]
            ring.AddPoint(x, y)
        ring.CloseRings()
        poly.AddGeometry(ring)

        # isole
        for isola in range(int(bordo['NUMEROISOLE'])):
            ring = Geometry(wkbLinearRing)
            for vertice in range(vertice + 1, vertice + 1 + tabisole[isola]):
                x, y = map(float, bordo['VERTICI'][vertice])
                if True:
                    x, y = trasformation.TransformPoint(x, y)[:2]
                ring.AddPoint(x, y)
            ring.CloseRings()
            poly.AddGeometry(ring)

        if len(bordo['CODICE IDENTIFICATIVO']) == 11:
            layer = layers['confini'][0]
        elif bordo['CODICE IDENTIFICATIVO'] == 'STRADA':
            layer = layers['strade'][0]
        elif bordo['CODICE IDENTIFICATIVO'] == 'ACQUA':
            layer = layers['acque'][0]
        elif bordo['CODICE IDENTIFICATIVO'][-1] == '+':
            layer = layers['edifici'][0]
        else:
            layer = layers['particelle'][0]
    
        feat = Feature(layer.GetLayerDefn())
        feat.SetField('comune', foglio['CODICE COMUNE'])
        feat.SetField('foglio', foglio['CODICE FOGLIO'])
        if bordo['CODICE IDENTIFICATIVO'][-1] == '+':
            feat.SetField('part', bordo['CODICE IDENTIFICATIVO'][:-1])
        else:
            feat.SetField('part', bordo['CODICE IDENTIFICATIVO'])
        feat.SetField('dimensione', int(bordo['DIMENSIONE']))
        pos_x, pos_y = map(float, (bordo['POSIZIONEX'], bordo['POSIZIONEY']))
        interno_x, interno_y = map(float, (bordo['PUNTOINTERNOX'], bordo['PUNTOINTERNOY']))
        if True:
            pos_x, pos_y = trasformation.TransformPoint(pos_x, pos_y)[:2]
            interno_x, interno_y = trasformation.TransformPoint(interno_x, interno_y)[:2]
        feat.SetField('pos_x', pos_x)
        feat.SetField('pos_y', pos_y)
        feat.SetField('interno_x', interno_x)
        feat.SetField('interno_y', interno_y)

        feat.SetGeometry(poly)
        layer.CreateFeature(feat)
        feat.Destroy()

    fiduciali_ds = GetDriverByName('ESRI Shapefile').CreateDataSource(join(outpath, 'fiduciali.shp'))
    fiduciali = fiduciali_ds.CreateLayer('strade', None, wkbPoint)

    f_numero = FieldDefn('numero', OFTString)
    f_numero.SetWidth(8)

    fiduciali.CreateField(f_comune)
    fiduciali.CreateField(f_foglio)
    fiduciali.CreateField(f_numero)

    for fiduciale in foglio['oggetti']['FIDUCIALE']:
        x, y = map(float, (fiduciale['POSIZIONEX'], fiduciale['POSIZIONEY']))
        if True:
            x, y = trasformation.TransformPoint(x, y)[:2]
        feat = Feature(fiduciali.GetLayerDefn())
        feat.SetField('comune', foglio['CODICE COMUNE'])
        feat.SetField('foglio', foglio['CODICE FOGLIO'])
        feat.SetField('numero', fiduciale['NUMERO IDENTIFICATIVO'])
        pt = Geometry(wkbPoint)
        pt.SetPoint_2D(0, x, y)
        feat.SetGeometry(pt)
        fiduciali.CreateFeature(feat)
        'PF%02d/%s%s/%s' % (int(fiduciale['NUMERO IDENTIFICATIVO']),
            foglio['CODICE NUMERO FOGLIO'][1:], foglio['CODICE ALLEGATO'], foglio['CODICE COMUNE'])


def tabisole(cxf, oggetto):
    oggetto['TABISOLE'] = []
    for isola in range(int(oggetto['NUMEROISOLE'])):
        oggetto['TABISOLE'].append(cxf.next().strip())

def vertici(cxf, oggetto):
    oggetto['VERTICI'] = []
    for vertice in range(int(oggetto['NUMEROVERTICI'])):
        oggetto['VERTICI'].append((cxf.next().strip(), cxf.next().strip()))

oggetti_cartografici = {
    'BORDO': (['CODICE IDENTIFICATIVO', 'DIMENSIONE', 'ANGOLO',
        'POSIZIONEX', 'POSIZIONEY', 'PUNTOINTERNOX', 'PUNTOINTERNOY',
        'NUMEROISOLE', 'NUMEROVERTICI'], [tabisole, vertici]),
    'TESTO': (['TESTO', 'DIMENSIONE', 'ANGOLO','POSIZIONEX', 'POSIZIONEY'], []),
    'SIMBOLO': (['CODICE SIMBOLO', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY'], []),
    'FIDUCIALE': (['NUMERO IDENTIFICATIVO', 'CODICE SIMBOLO', 'POSIZIONEX', 'POSIZIONEY',
        'PUNTORAPPRESENTAZIONEX', 'PUNTORAPPRESENTAZIONEY'], []),
    'LINEA': (['CODICE TIPO DI TRATTO', 'NUMEROVERTICI'], [vertici]),
    'EOF': ([], []),
}


def do_main(basepath):
    foglio = {}

    basename = path_basename(basepath).upper()
    
    # check basename
    assert len(basename) == 11

    foglio['CODICE FOGLIO'] = basename
    foglio['CODICE COMUNE'] = basename[:4]
    foglio['CODICE SEZIONE CENSUARIA'] = basename[4]
    assert foglio['CODICE SEZIONE CENSUARIA'] in ['A', 'B', '_']
    
    foglio['CODICE NUMERO FOGLIO'] = basename[5:9]
    foglio['NUMERO FOGLIO'] = foglio['CODICE NUMERO FOGLIO'].lstrip('0')

    foglio['CODICE ALLEGATO'] = basename[9]
    assert foglio['CODICE ALLEGATO'] in ['0', 'Q'] # missing

    foglio['CODICE SVILUPPO'] = basename[10]
    assert foglio['CODICE SVILUPPO'] in ['0', 'U']
    
    cxf = open(basepath + '.CXF')
    sup = open(basepath + '.SUP')

    # parse header
    foglio['header'] = {}
    header = foglio['header']
    header['MAPPA'] = cxf.next().strip()
    assert header['MAPPA'] in ['MAPPA', 'MAPPA FONDIARIO', 'QUADRO D\'UNIONE']

    header['NOME MAPPA'] = cxf.next().strip()
    assert header['NOME MAPPA'] == basename
    
    header['SCALA ORIGINARIA'] = cxf.next().strip()

    foglio['oggetti'] = dict((object_name, []) for object_name in oggetti_cartografici)

    for raw_line in cxf:
        line = raw_line.strip().rstrip('\\')
        assert line in oggetti_cartografici, 'Unknown object %r' % line

        oggetto = {}
        nomi_record, parse_functions = oggetti_cartografici[line]
        for nome_record in nomi_record:
            oggetto[nome_record] = cxf.next().strip()

        for parse_function in parse_functions:
            parse_function(cxf, oggetto)

        foglio['oggetti'][line].append(oggetto)

        if line == 'EOF':
            # record di terminazione
            break

    garbage = cxf.readline()
    assert garbage == '', 'Garbage after EOF %r' % garbage

    foglio_to_shapefiles(foglio, basepath)


def main():
    do_main(sys.argv[1])


if __name__ == '__main__':
    main()
