
from os.path import basename as path_basename


def parse_censuario(basepath):
    censuario = {}

    basename = path_basename(basepath).upper()

    # check basename
    assert len(basename) == 7 or len(basename) == 8, basename

    censuario['CODICE_COMUNE'] = basename[:4]
    if len(basename) == 8:
        censuario['SEZIONE'] = basename[4]
    censuario['IDENTIFICATIVO RICHIESTA'] = basename[-4:]

    censuario['FABBRICATI'] = {}

    try:
        fab = open(basepath + '.FAB')
    except:
        fab = ()

    for i, raw_line in enumerate(fab):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        oggetto['IDENTIFICATIVO_IMMOBILE'], tipo_immobile, oggetto['PROGRESSIVO'], oggetto['TIPO_RECORD'] = fields[2:6]
        assert tipo_immobile == 'F'
        assert oggetto['TIPO_RECORD'] in ['1', '2', '3', '4', '5']
        if oggetto['TIPO_RECORD'] == '1':
            record_len = 40
            oggetto['ZONE'], oggetto['CATEGORIA'], oggetto['CLASSE'], oggetto['CONSISTENZA'], oggetto['SUPERFICIE'] = fields[6:11]
            oggetto['RENDITA'] = fields[12]
        elif oggetto['TIPO_RECORD'] == '2':
            record_len = 13
            oggetto['SEZIONE URBANA'], oggetto['FOGLIO'], oggetto['NUMERO'], oggetto['DENOMINATORE'], oggetto['SUBALTERNO'], oggetto['EDIFICIALITA'] = fields[6:12]
            fields = fields[:13]
        else:
            continue

        assert len(fields) == record_len, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO_RECORD'], len(fields),  record)

        censuario['FABBRICATI'][oggetto['IDENTIFICATIVO_IMMOBILE']] = {}
        censuario['FABBRICATI'][oggetto['IDENTIFICATIVO_IMMOBILE']].update(oggetto)

    censuario['TERRENI'] = {}

    try:
        ter = open(basepath + '.TER')
    except:
        ter = ()

    for i, raw_line in enumerate(ter):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        oggetto['IDENTIFICATIVO_IMMOBILE'], tipo_immobile, oggetto['PROGRESSIVO'], oggetto['TIPO_RECORD'] = fields[2:6]
        assert tipo_immobile == 'T'
        assert oggetto['TIPO_RECORD'] in ['1', '2', '3', '4']
        if oggetto['TIPO_RECORD'] == '1':
            record_len = 40
            oggetto['FOGLIO'], oggetto['NUMERO'], oggetto['DENOMINATORE'], oggetto['SUBALTERNO'], oggetto['EDIFICIALITA'] = fields[6:11]
            oggetto['QUALITA'], oggetto['CLASSE'], oggetto['ETTARI'], oggetto['ARE'], oggetto['CENTIARE'] = fields[11:16]
            oggetto['REDDITO_DOMINICALE'], oggetto['REDDITO_AGRICOLO'] = fields[21:23]
        else:
            continue

        assert len(fields) == record_len, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO RECORD'], len(fields),  record)

        censuario['TERRENI'][oggetto['IDENTIFICATIVO_IMMOBILE']] = oggetto

    censuario['SOGGETTI'] = {}

    sog = open(basepath + '.SOG')

    for i, raw_line in enumerate(sog):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        oggetto['IDENTIFICATIVO_SOGGETTO'], oggetto['TIPO_SOGGETTO'] = fields[2:4]
        assert oggetto['TIPO_SOGGETTO'] in ['P', 'G'], oggetto['TIPO_SOGGETTO']
        if oggetto['TIPO_SOGGETTO'] == 'P':
            record_len = 12
            oggetto['COGNOME'], oggetto['NOME'], oggetto['SESSO'], oggetto['DATA_DI_NASCITA'], oggetto['LUOGO_DI_NASCITA'], oggetto['CODICE FISCALE'] = fields[6:12]
        elif oggetto['TIPO_SOGGETTO'] == 'G':
            record_len = 8
            oggetto['DENOMINAZIONE'], oggetto['SEDE'], oggetto['CODICE_FISCALE'] = fields[4:7]

        assert len(fields) == record_len, 'Anomalous record schema line: %d, type: %r, len: %d, record: %r' % (i + 1, oggetto['TIPO SOGGETTO'], len(fields),  record)

        identificativo_soggetto = oggetto['IDENTIFICATIVO_SOGGETTO'], oggetto['TIPO_SOGGETTO']
        censuario['SOGGETTI'][identificativo_soggetto] = oggetto

    censuario['TITOLARITA'] = []

    tit = open(basepath + '.TIT')

    for i, raw_line in enumerate(tit):
        record = raw_line.strip()
        fields = record.split('|')
        oggetto = {}
        tit = tuple(fields[2:6])
        censuario['TITOLARITA'].append(tit)

    return censuario

