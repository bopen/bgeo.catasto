
from os import mkdir
from os.path import join, basename as path_basename, splitext
import sys

from osgeo.osr import CoordinateTransformation, SpatialReference
from osgeo.ogr import GetDriverByName, wkbPoint, wkbPolygon, wkbLinearRing, Feature, Geometry, FieldDefn
from osgeo.ogr import OFTString, OFTInteger, OFTReal

local_cassini_soldener = SpatialReference()
# local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0.8 +y_0=-1.3 +ellps=intl +units=m +no_defs')
local_cassini_soldener.ImportFromProj4(
    '+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0 +y_0=0 +ellps=intl +units=m +no_defs'
)
gauss_boaga_ovest = SpatialReference()
#gauss_boaga_ovest.ImportFromProj4(
#    '+proj=tmerc +lat_0=0 +lon_0=15 +k=0.9996 +x_0=2520000 +y_0=0 +ellps=intl +units=m +no_defs +towgs84=-104.0,-51.3,-8.4,0.971,-2.917,0.714,-11.68'
#)
gauss_boaga_ovest.ImportFromEPSG(3004)

trasformation = CoordinateTransformation(local_cassini_soldener, gauss_boaga_ovest)


def foglio_to_shapefiles(foglio, outpath):
    mkdir(outpath)

    f_comune = FieldDefn('comune', OFTString)
    f_comune.SetWidth(4)
    f_foglio = FieldDefn('foglio', OFTString)
    f_foglio.SetWidth(11)
    f_tipo = FieldDefn('tipo', OFTString)
    f_tipo.SetWidth(11)
    f_part = FieldDefn('part', OFTString)
    f_part.SetWidth(8)
    f_dimensione = FieldDefn('dimensione', OFTInteger)
    f_angolo = FieldDefn('angolo', OFTReal)
    f_pos_x = FieldDefn('pos_x', OFTReal)
    f_pos_y = FieldDefn('pos_y', OFTReal)
    f_interno_x = FieldDefn('interno_x', OFTReal)
    f_interno_y = FieldDefn('interno_y', OFTReal)

    ds = GetDriverByName('ESRI Shapefile').CreateDataSource(join(outpath, 'bordi.shp'))
    bordi = ds.CreateLayer('bordi', gauss_boaga_ovest, wkbPolygon)

    bordi.CreateField(f_comune)
    bordi.CreateField(f_foglio)
    bordi.CreateField(f_tipo)
    bordi.CreateField(f_part)
    bordi.CreateField(f_dimensione)
    bordi.CreateField(f_angolo)
    bordi.CreateField(f_pos_x)
    bordi.CreateField(f_pos_y)
    bordi.CreateField(f_interno_x)
    bordi.CreateField(f_interno_y)

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
            tipo = 'CONFINE'
        elif bordo['CODICE IDENTIFICATIVO'] == 'STRADA':
            tipo = 'STRADA'
        elif bordo['CODICE IDENTIFICATIVO'] == 'ACQUA':
            tipo = 'ACQUA'
        elif bordo['CODICE IDENTIFICATIVO'][-1] == '+':
            tipo = 'FABBRICATO'
        else:
            tipo = 'PARTICELLA'
    
        feat = Feature(bordi.GetLayerDefn())
        feat.SetField('comune', foglio['CODICE COMUNE'])
        feat.SetField('foglio', foglio['CODICE FOGLIO'])
        feat.SetField('tipo', tipo)
        feat.SetField('part', bordo['CODICE IDENTIFICATIVO'])
        feat.SetField('dimensione', int(bordo['DIMENSIONE']))
        feat.SetField('angolo', float(bordo['ANGOLO']))
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
        bordi.CreateFeature(feat)
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

