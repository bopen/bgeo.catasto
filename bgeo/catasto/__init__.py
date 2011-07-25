
from os.path import basename as path_basename

from osgeo.osr import CoordinateTransformation, SpatialReference


local_cassini_soldener = SpatialReference()
# local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0.8 +y_0=-1.3 +ellps=intl +units=m +no_defs')
local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0 +y_0=0 +ellps=intl +units=m +no_defs')
gauss_boaga_ovest = SpatialReference()
gauss_boaga_ovest.ImportFromEPSG(3004)

trasformation = CoordinateTransformation(local_cassini_soldener, gauss_boaga_ovest)

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
    'FIDUCIALE': (['NUMERO IDENTIFICATIVO', 'CODICE SIMBOLO', 'POSIZIONEX', 'POSIZIONEY',
        'PUNTORAPPRESENTAZIONEX', 'PUNTORAPPRESENTAZIONEY'], []),
    'SIMBOLO': (['CODICE SIMBOLO', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY'], []),
    'LINEA': (['CODICE TIPO DI TRATTO', 'NUMEROVERTICI'], [vertici]),
    'EOF': ([], []),
}


def do_main(basepath):
    foglio = {}

    basename = path_basename(basepath).upper()
    
    # check basename
    assert len(basename) == 11
    
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

#        if len(oggetto['CODICE IDENTIFICATIVO']) == 11:
#            print '*** CONFINE', elemento['CODICE IDENTIFICATIVO']
#        elif oggetto['CODICE IDENTIFICATIVO'] == 'STRADA':
#            print '*** STRADA', elemento['CODICE IDENTIFICATIVO']
#        elif oggetto['CODICE IDENTIFICATIVO'] == 'ACQUA':
#            print '*** FABBRICATO', elemento['CODICE IDENTIFICATIVO']
#        elif oggetto['CODICE IDENTIFICATIVO'].endswith('+'):
#            print '*** FABBRICATO in PARTICELLA', elemento['CODICE IDENTIFICATIVO'][:-1]
#        else:
#            print '*** PARTICELLA', elemento['CODICE IDENTIFICATIVO']


#            print 'FIDUCIALE', 'PF%02d/%s%s/%s' % (int(elemento['NUMERO IDENTIFICATIVO']), codice_numero_foglio[1:], codice_allegato, codice_comune)
#            x,  y = float(elemento['POSIZIONEX']), float(elemento['POSIZIONEY'])
#            print x, y, trasformation.TransformPoint(x, y)[:2]
        if line == 'EOF':
            # record di terminazione
            break

    garbage = cxf.readline()
    assert garbage == '', 'Garbage after EOF %r' % garbage

    # print foglio


def main():
    do_main('E259_004900')


if __name__ == '__main__':
    main()
