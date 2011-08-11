
from os.path import basename as path_basename


def parse_censuario(basepath):
    censuario = {}

    basename = path_basename(basepath).upper()

    # check basename
    assert len(basename) == 7 or len(basename) == 8, basename

    censuario['CODICE COMUNE'] = basename[:4]
    if len(basename) == 8:
        censuario['SEZIONE'] = basename[4]
    censuario['IDENTIFICATIVO RICHIESTA'] = basename[-4:]

    censuario['TERRENI'] = {}

    ter = open(basepath + '.TER')

    for i, raw_line in enumerate(ter):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        oggetto['IDENTIFICATIVO IMMOBILE'], tipo_immobile, oggetto['PROGRESSIVO'], oggetto['TIPO RECORD'] = fields[2:6]
        assert tipo_immobile == 'T'
        assert oggetto['TIPO RECORD'] in ['1', '2', '3', '4']
        if oggetto['TIPO RECORD'] == '1':
            record_len = 40
            oggetto['FOGLIO'], oggetto['NUMERO'], oggetto['DENOMINATORE'], oggetto['SUBALTERNO'], oggetto['EDIFICIALITA'] = fields[6:11]
        else:
            continue

        assert len(fields) == record_len, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO RECORD'], len(fields),  record)

        censuario['TERRENI'][oggetto['IDENTIFICATIVO IMMOBILE']] = oggetto

    censuario['SOGGETTI'] = {}

    sog = open(basepath + '.SOG')

    for i, raw_line in enumerate(sog):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        oggetto['IDENTIFICATIVO SOGGETTO'], oggetto['TIPO SOGGETTO'] = fields[2:4]
        assert oggetto['TIPO SOGGETTO'] in ['P', 'G'], oggetto['TIPO SOGGETTO']
        if oggetto['TIPO SOGGETTO'] == 'P':
            record_len = 12
            oggetto['COGNOME'], oggetto['NOME'], oggetto['SESSO'], oggetto['DATA DI NASCITA'], oggetto['LUOGO DI NASCITA'], oggetto['CODICE FISCALE'] = fields[6:12]
        elif oggetto['TIPO SOGGETTO'] == 'G':
            record_len = 8
            oggetto['DENOMINAZIONE'], oggetto['SEDE'], oggetto['CODICE FISCALE'] = fields[4:7]

        assert len(fields) == record_len, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO SOGGETTO'], len(fields),  record)

        identificativo_soggetto = oggetto['IDENTIFICATIVO SOGGETTO'], oggetto['TIPO SOGGETTO']
        censuario['SOGGETTI'][identificativo_soggetto] = oggetto

    tit = open(basepath + '.TIT')
    
    for i, raw_line in enumerate(tit):
        record = raw_line.strip()
        fields = record.split('|')
        if fields[0] != censuario['CODICE COMUNE']:
            print 'skipping', record
            continue
        oggetto = {}
        oggetto['IDENTIFICATIVO SOGGETTO'], oggetto['TIPO SOGGETTO'], oggetto['IDENTIFICATIVO IMMOBILE'], oggetto['TIPO IMMOBILE'] = fields[2:6]
    
        if oggetto['TIPO IMMOBILE'] == 'F':
            continue

        immobile = censuario['TERRENI'][oggetto['IDENTIFICATIVO IMMOBILE']]
        identificativo_soggetto = oggetto['IDENTIFICATIVO SOGGETTO'], oggetto['TIPO SOGGETTO']
        soggetto = censuario['SOGGETTI'][identificativo_soggetto]

        if soggetto.get('DENOMINAZIONE', '').find('INDU') >= 0:
            print soggetto['DENOMINAZIONE'], immobile['FOGLIO'], immobile['NUMERO']

        assert len(fields) == 29 or len(fields) == 8 or len(fields) == 22, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO SOGGETTO'], len(fields),  record)


    return censuario

