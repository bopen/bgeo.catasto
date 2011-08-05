
from os import mkdir
from os.path import join, basename as path_basename
import sys


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

    return foglio

