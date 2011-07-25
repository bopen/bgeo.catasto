
from os.path import basename as path_basename

from osgeo.osr import CoordinateTransformation, SpatialReference


local_cassini_soldener = SpatialReference()
# local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0.8 +y_0=-1.3 +ellps=intl +units=m +no_defs')
local_cassini_soldener.ImportFromProj4('+proj=cass +lat_0=41.650375 +lon_0=14.259775 +x_0=0 +y_0=0 +ellps=intl +units=m +no_defs')
gauss_boaga_ovest = SpatialReference()
gauss_boaga_ovest.ImportFromEPSG(3004)

trasformation = CoordinateTransformation(local_cassini_soldener, gauss_boaga_ovest)


oggetti_cartografici = {
    'BORDO': ['CODICE IDENTIFICATIVO', 'DIMENSIONE', 'ANGOLO',
        'POSIZIONEX', 'POSIZIONEY', 'PUNTOINTERNOX', 'PUNTOINTERNOY',
        'NUMEROISOLE', 'NUMEROVERTICI', isole, vertici],
    'TESTO': ['TESTO', 'DIMENSIONE', 'ANGOLO','POSIZIONEX', 'POSIZIONEY'],
}
['BORDO', 'TESTO', 'SIMBOLO', 'FIDUCIALE', 'LINEA', 'EOF']


def do_main(basepath):
    basename = path_basename(basepath).upper()
    
    # check basename
    assert len(basename) == 11
    
    codice_comune = basename[:4]
    codice_sezione_censuaria = basename[4]
    assert codice_sezione_censuaria in ['A', 'B', '_']
    
    codice_numero_foglio = basename[5:9]
    numero_foglio = codice_numero_foglio.lstrip('0')

    codice_allegato = basename[9]
    assert codice_allegato in ['0', 'Q'] # missing

    codice_sviluppo = basename[10]
    assert codice_sviluppo in ['0', 'U']
    
    cxf = open(basepath + '.CXF')
    sup = open(basepath + '.SUP')

    # parse header
    mappa = cxf.next().strip()
    assert mappa in ['MAPPA', 'MAPPA FONDIARIO', 'QUADRO D\'UNIONE']

    nome_mappa = cxf.next().strip()
    assert nome_mappa  == basename
    
    scala_originaria = cxf.next().strip()

    for raw_line in cxf:
        line = raw_line.strip().rstrip('\\')
        assert line in oggetti_cartografici.keys(), line
        
        if line == 'BORDO':
            elemento = {}
            for nome_record in ['CODICE IDENTIFICATIVO', 'DIMENSIONE', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY',
                    'PUNTOINTERNOX', 'PUNTOINTERNOY', 'NUMEROISOLE', 'NUMEROVERTICI']:
                elemento[nome_record] = cxf.next().strip()
            if len(elemento['CODICE IDENTIFICATIVO']) == 11:
                print '*** CONFINE', elemento['CODICE IDENTIFICATIVO']
            elif elemento['CODICE IDENTIFICATIVO'] == 'STRADA':
                print '*** STRADA', elemento['CODICE IDENTIFICATIVO']
            elif elemento['CODICE IDENTIFICATIVO'] == 'ACQUA':
                print '*** FABBRICATO', elemento['CODICE IDENTIFICATIVO']
            elif elemento['CODICE IDENTIFICATIVO'].endswith('+'):
                print '*** FABBRICATO in PARTICELLA', elemento['CODICE IDENTIFICATIVO'][:-1]
            else:
                print '*** PARTICELLA', elemento['CODICE IDENTIFICATIVO']
            for isola in range(int(elemento['NUMEROISOLE'])):
                cxf.next().strip()
            for vertice in range(int(elemento['NUMEROVERTICI'])):
                cxf.next().strip(), cxf.next().strip()
        elif line == 'FIDUCIALE':
            elemento = {}
            for nome_record in ['NUMERO IDENTIFICATIVO', 'CODICE SIMBOLO', 'POSIZIONEX', 'POSIZIONEY',
                    'PUNTORAPPRESENTAZIONEX', 'PUNTORAPPRESENTAZIONEY']:
                elemento[nome_record] = cxf.next().strip()
            print 'FIDUCIALE', 'PF%02d/%s%s/%s' % (int(elemento['NUMERO IDENTIFICATIVO']), codice_numero_foglio[1:], codice_allegato, codice_comune)
            x,  y = float(elemento['POSIZIONEX']), float(elemento['POSIZIONEY'])
            print x, y, trasformation.TransformPoint(x, y)[:2]
        elif line == 'LINEA':
            elemento = {}
            for nome_record in ['CODICE TIPO DI TRATTO', 'NUMEROVERTICI']:
                elemento[nome_record] = cxf.next().strip()
            for vertice in range(int(elemento['NUMEROVERTICI'])):
                cxf.next().strip(), cxf.next().strip()
        elif line == 'SIMBOLO':
            elemento = {}
            for nome_record in ['CODICE SIMBOLO', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY']:
                elemento[nome_record] = cxf.next().strip()
        elif line == 'TESTO':
            elemento = {}
            for nome_record in ['TESTO', 'DIMENSIONE', 'ANGOLO','POSIZIONEX', 'POSIZIONEY']:
                elemento[nome_record] = cxf.next().strip()
        elif line == 'EOF':
            # record di terminazione
            break
    
    assert cxf.readline() == ''
    

def main():
    do_main('E259_004900')


if __name__ == '__main__':
    main()
