
from os.path import basename as path_basename


def tabisole(cxf, oggetto):
    oggetto['TABISOLE'] = []
    for isola in range(int(oggetto['NUMEROISOLE'])):
        oggetto['TABISOLE'].append(cxf.next().strip())


def vertici(cxf, oggetto):
    oggetto['VERTICI'] = []
    for vertice in range(int(oggetto['NUMEROVERTICI'])):
        oggetto['VERTICI'].append((cxf.next().strip(), cxf.next().strip()))


def tipo(cxf, oggetto):
    if len(oggetto['CODICE IDENTIFICATIVO']) == 11:
        tipo = 'CONFINE'
    elif oggetto['CODICE IDENTIFICATIVO'] == 'STRADA':
        tipo = 'STRADA'
    elif oggetto['CODICE IDENTIFICATIVO'] == 'ACQUA':
        tipo = 'ACQUA'
    elif oggetto['CODICE IDENTIFICATIVO'][-1] == '+':
        tipo = 'FABBRICATO'
    else:
        tipo = 'PARTICELLA'
    oggetto['tipo'] = tipo


oggetti_cartografici = {
    'BORDO': ([
        'CODICE IDENTIFICATIVO', 'DIMENSIONE', 'ANGOLO',
        'POSIZIONEX', 'POSIZIONEY', 'PUNTOINTERNOX', 'PUNTOINTERNOY',
        'NUMEROISOLE', 'NUMEROVERTICI'
    ], [tabisole, vertici, tipo]),
    'TESTO': (['TESTO', 'DIMENSIONE', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY'], []),
    'SIMBOLO': (['CODICE SIMBOLO', 'ANGOLO', 'POSIZIONEX', 'POSIZIONEY'], []),
    'FIDUCIALE': ([
        'NUMERO IDENTIFICATIVO', 'CODICE SIMBOLO', 'POSIZIONEX', 'POSIZIONEY',
        'PUNTORAPPRESENTAZIONEX', 'PUNTORAPPRESENTAZIONEY'], []),
    'LINEA': (['CODICE TIPO DI TRATTO', 'NUMEROVERTICI'], [vertici]),
    'EOF': ([], []),
}


def parse_foglio(basepath):
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
    assert foglio['CODICE ALLEGATO'] in ['0', 'Q']  # missing

    foglio['CODICE SVILUPPO'] = basename[10]
    assert foglio['CODICE SVILUPPO'] in ['0', 'U']

    cxf = open(basepath + '.CXF')
    sup = open(basepath + '.SUP')

    # parse CXF
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

    try:
        garbage = cxf.next()
    except StopIteration:
        garbage = None
    assert garbage is None, 'Garbage after CXF EOF %r' % garbage

    # parse SUP
    name, date_update = next(sup).split()

    def check(sup, key_name, tipo):
        key, value = next(sup).split()
        assert key == key_name
        check = int(value)
        oggetti = sum(1 for b in foglio['oggetti']['BORDO'] if b['tipo'] == tipo)
        print key, value
        assert oggetti == check

    check(sup, 'N.FABBRIC', 'FABBRICATO')
    check(sup, 'N.PARTIC', 'PARTICELLA')
    check(sup, 'N.STRADE', 'STRADA')
    check(sup, 'N.ACQUE', 'ACQUA')

    next(sup)
    next(sup)

    areas = dict(next(sup).split() for b in foglio['oggetti']['BORDO'] if b['tipo'] == 'PARTICELLA')

    for b in foglio['oggetti']['BORDO']:
        if b['tipo'] != 'PARTICELLA':
            continue
        b['AREA'] = int(areas[b['CODICE IDENTIFICATIVO']])

    key, value = next(sup).split()
    assert key == 'PARTIC', (key, value)
    check = int(value)
    area = sum(int(a) for a in areas.values())
    print key, value
    assert check * 0.95 < area < check * 1.05, (area, check)

    for i in range(6):
        next(sup)

    try:
        garbage = next(sup)
    except StopIteration:
        garbage = None
    assert garbage is None, 'Garbage after SUP EOF %r' % garbage

    return foglio
