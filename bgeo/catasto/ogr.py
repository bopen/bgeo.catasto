
from os import mkdir
from os.path import join, basename as path_basename, splitext
import sys

from osgeo.osr import CoordinateTransformation, SpatialReference
from osgeo.ogr import wkbPoint, wkbPolygon, wkbLinearRing, wkbLineString
from osgeo.ogr import GetDriverByName, Feature, Geometry, FieldDefn
from osgeo.ogr import OFTString, OFTInteger, OFTReal


cassini_soldener = '+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=%f +y_0=%f +ellps=intl +units=m +no_defs'

comuni_shift = {
    'B550': (12.8, 16.8),
    'L113': (-58.8, -8.6),
}


def write_foglio(foglio, destination, format_name='ESRI Shapefile', t_srs='3004'):
    
    target_srs = SpatialReference()
    try:
        target_srs.ImportFromEPSG(int(t_srs))
    except TypeError:
        raise
        target_srs.ImportFromProj4(t_srs)

    local_cassini_soldener = cassini_soldener % comuni_shift.get(foglio['CODICE COMUNE'], (0, 0))

    source_srs = SpatialReference()
    source_srs.ImportFromProj4(local_cassini_soldener)

    trasformation = CoordinateTransformation(source_srs, target_srs)

    f_comune = FieldDefn('COMUNE', OFTString)
    f_comune.SetWidth(4)
    f_foglio = FieldDefn('FOGLIO', OFTString)
    f_foglio.SetWidth(11)
    f_tipo = FieldDefn('tipo', OFTString)
    f_tipo.SetWidth(11)
    f_part = FieldDefn('PARTICELLA', OFTString)
    f_part.SetWidth(8)
    f_numero = FieldDefn('NUMERO', OFTString)
    f_part.SetWidth(8)
    f_dimensione = FieldDefn('DIMENSIONE', OFTInteger)
    f_area = FieldDefn('AREA', OFTInteger)
    f_angolo = FieldDefn('ANGOLO', OFTReal)
    f_pos_x = FieldDefn('POSIZIONEX', OFTReal)
    f_pos_y = FieldDefn('POSIZIONEY', OFTReal)
    f_interno_x = FieldDefn('P_INTERNOX', OFTReal)
    f_interno_y = FieldDefn('P_INTERNOY', OFTReal)
    f_simbolo = FieldDefn('SIMBOLO', OFTInteger)
    f_etichetta = FieldDefn('etichetta', OFTString)
    f_etichetta.SetWidth(32)
    f_testo = FieldDefn('TESTO', OFTString)
    f_testo.SetWidth(256)

    ds = GetDriverByName(format_name).CreateDataSource(destination)

    # tipo BORDO
    bordi = ds.CreateLayer('BORDI', target_srs, wkbPolygon)

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
    bordi.CreateField(f_area)
    bordi.CreateField(f_etichetta)

    for oggetto in foglio['oggetti']['BORDO']:
        poly = Geometry(wkbPolygon)
        tabisole = map(int, oggetto['TABISOLE'])

        # contorno esterno
        vertici_contorno = int(oggetto['NUMEROVERTICI']) - sum(tabisole)
        ring = Geometry(wkbLinearRing)
        for vertice in range(vertici_contorno):
            x, y = map(float, oggetto['VERTICI'][vertice])
            if True:
                x, y = trasformation.TransformPoint(x, y)[:2]
            ring.AddPoint(x, y)
        ring.CloseRings()
        poly.AddGeometry(ring)

        # isole
        for isola in range(int(oggetto['NUMEROISOLE'])):
            ring = Geometry(wkbLinearRing)
            for vertice in range(vertice + 1, vertice + 1 + tabisole[isola]):
                x, y = map(float, oggetto['VERTICI'][vertice])
                if True:
                    x, y = trasformation.TransformPoint(x, y)[:2]
                ring.AddPoint(x, y)
            ring.CloseRings()
            poly.AddGeometry(ring)

        etichetta = oggetto['CODICE IDENTIFICATIVO']
        if oggetto['CODICE IDENTIFICATIVO'][-1] == '+':
            etichetta = ''

        feat = Feature(bordi.GetLayerDefn())
        feat.SetField('COMUNE', foglio['CODICE COMUNE'])
        feat.SetField('FOGLIO', foglio['CODICE FOGLIO'])
        feat.SetField('tipo', oggetto['tipo'])
        feat.SetField('PARTICELLA', oggetto['CODICE IDENTIFICATIVO'])
        feat.SetField('DIMENSIONE', int(oggetto['DIMENSIONE']))
        feat.SetField('ANGOLO', float(oggetto['ANGOLO']))
        pos_x, pos_y = map(float, (oggetto['POSIZIONEX'], oggetto['POSIZIONEY']))
        interno_x, interno_y = map(float, (oggetto['PUNTOINTERNOX'],oggetto['PUNTOINTERNOY']))
        if True:
            pos_x, pos_y = trasformation.TransformPoint(pos_x, pos_y)[:2]
            interno_x, interno_y = trasformation.TransformPoint(interno_x, interno_y)[:2]
        feat.SetField('POSIZIONEX', pos_x)
        feat.SetField('POSIZIONEY', pos_y)
        feat.SetField('P_INTERNOX', interno_x)
        feat.SetField('P_INTERNOY', interno_y)
        feat.SetField('AREA', oggetto.get('AREA', -1))
        feat.SetField('etichetta', etichetta)
        feat.SetGeometry(poly)
        bordi.CreateFeature(feat)
        feat.Destroy()


    # tipo TESTO
    testi = ds.CreateLayer('TESTI', target_srs, wkbPoint)

    testi.CreateField(f_comune)
    testi.CreateField(f_foglio)
    testi.CreateField(f_testo)
    testi.CreateField(f_dimensione)
    testi.CreateField(f_angolo)
    testi.CreateField(f_etichetta)

    for oggetto in foglio['oggetti']['TESTO']:
        x, y = map(float, (oggetto['POSIZIONEX'], oggetto['POSIZIONEY']))
        if True:
            x, y = trasformation.TransformPoint(x, y)[:2]
        # FIXME: many texts are useless, prun them from etichetta
        etichetta = oggetto['TESTO']
        
        feat = Feature(testi.GetLayerDefn())
        feat.SetField('COMUNE', foglio['CODICE COMUNE'])
        feat.SetField('FOGLIO', foglio['CODICE FOGLIO'])
        feat.SetField('TESTO', oggetto['TESTO'])
        feat.SetField('DIMENSIONE', int(oggetto['DIMENSIONE']))
        feat.SetField('ANGOLO', float(oggetto['ANGOLO']))
        feat.SetField('etichetta', etichetta)
        pt = Geometry(wkbPoint)
        pt.SetPoint_2D(0, x, y)
        feat.SetGeometry(pt)
        testi.CreateFeature(feat)


    # tipo SIMBOLO
    simboli = ds.CreateLayer('SIMBOLI', target_srs, wkbPoint)

    simboli.CreateField(f_comune)
    simboli.CreateField(f_foglio)
    simboli.CreateField(f_simbolo)
    simboli.CreateField(f_angolo)

    for oggetto in foglio['oggetti']['SIMBOLO']:
        x, y = map(float, (oggetto['POSIZIONEX'], oggetto['POSIZIONEY']))
        if True:
            x, y = trasformation.TransformPoint(x, y)[:2]
        
        feat = Feature(simboli.GetLayerDefn())
        feat.SetField('COMUNE', foglio['CODICE COMUNE'])
        feat.SetField('FOGLIO', foglio['CODICE FOGLIO'])
        feat.SetField('SIMBOLO', oggetto['CODICE SIMBOLO'])
        feat.SetField('ANGOLO', float(oggetto['ANGOLO']))
        pt = Geometry(wkbPoint)
        pt.SetPoint_2D(0, x, y)
        feat.SetGeometry(pt)
        simboli.CreateFeature(feat)


    # tipo FIDUCIALE
    fiduciali = ds.CreateLayer('FIDUCIALI', target_srs, wkbPoint)

    fiduciali.CreateField(f_comune)
    fiduciali.CreateField(f_foglio)
    fiduciali.CreateField(f_numero)
    fiduciali.CreateField(f_simbolo)
    fiduciali.CreateField(f_pos_x)
    fiduciali.CreateField(f_pos_y)
    fiduciali.CreateField(f_etichetta)

    for oggetto in foglio['oggetti']['FIDUCIALE']:
        x, y = map(float, (oggetto['POSIZIONEX'], oggetto['POSIZIONEY']))
        pos_x, pos_y = map(float, (oggetto['PUNTORAPPRESENTAZIONEX'], oggetto['PUNTORAPPRESENTAZIONEY']))
        if True:
            x, y = trasformation.TransformPoint(x, y)[:2]
            pos_x, pos_y = trasformation.TransformPoint(pos_x, pos_y)[:2]
        etichetta = 'PF%02d/%s%s/%s' % (int(oggetto['NUMERO IDENTIFICATIVO']),
            foglio['CODICE NUMERO FOGLIO'][1:], foglio['CODICE ALLEGATO'], foglio['CODICE COMUNE'])
        
        feat = Feature(fiduciali.GetLayerDefn())
        feat.SetField('COMUNE', foglio['CODICE COMUNE'])
        feat.SetField('FOGLIO', foglio['CODICE FOGLIO'])
        feat.SetField('NUMERO', oggetto['NUMERO IDENTIFICATIVO'])
        feat.SetField('SIMBOLO', oggetto['CODICE SIMBOLO'])
        feat.SetField('POSIZIONEX', pos_x)
        feat.SetField('POSIZIONEY', pos_y)
        feat.SetField('etichetta', etichetta)
        pt = Geometry(wkbPoint)
        pt.SetPoint_2D(0, x, y)
        feat.SetGeometry(pt)
        fiduciali.CreateFeature(feat)

        print etichetta, oggetto['POSIZIONEX'], oggetto['POSIZIONEY'], x, y


    # tipo LINEA
    linee = ds.CreateLayer('LINEE', target_srs, wkbLineString)

    linee.CreateField(f_comune)
    linee.CreateField(f_foglio)
    linee.CreateField(f_simbolo)

    for oggetto in foglio['oggetti']['LINEA']:
        # contorno esterno
        vertici = int(oggetto['NUMEROVERTICI'])
        linea = Geometry(wkbLineString)
        for vertice in range(vertici):
            x, y = map(float, oggetto['VERTICI'][vertice])
            if True:
                x, y = trasformation.TransformPoint(x, y)[:2]
            linea.AddPoint(x, y)

        feat = Feature(linee.GetLayerDefn())
        feat.SetField('COMUNE', foglio['CODICE COMUNE'])
        feat.SetField('FOGLIO', foglio['CODICE FOGLIO'])
        feat.SetField('SIMBOLO', oggetto['CODICE TIPO DI TRATTO'])
        feat.SetGeometry(linea)
        linee.CreateFeature(feat)
        feat.Destroy()
    
    ds.Destroy()
