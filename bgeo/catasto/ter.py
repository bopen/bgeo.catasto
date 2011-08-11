
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

    censuario['terreni'] = []

    print censuario

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

        censuario['terreni'].append(oggetto)

    return censuario

