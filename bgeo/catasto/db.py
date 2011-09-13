
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, Unicode

Base = declarative_base()


class Particella(Base):
    __tablename__ = 'catasto_particelle'

    id = Column(Integer, primary_key=True)
    comune = Column(Unicode())
    foglio = Column(Unicode())
    tipo = Column(Unicode())
    particella = Column(Unicode())
    QUALITA = Column(Unicode())
    CLASSE = Column(Unicode())
    ETTARI = Column(Unicode())
    ARE = Column(Unicode())
    CENTIARE = Column(Unicode())
    REDDITO_DOMINICALE = Column(Unicode())
    REDDITO_AGRICOLO = Column(Unicode())


class Soggetti(Base):
    __tablename__ = 'catasto_soggetti'

    id = Column(Integer, primary_key=True)
    CODICE_COMUNE = Column(Unicode())
    IDENTIFICATIVO_SOGGETTO = Column(Unicode())
    TIPO_SOGGETTO = Column(Unicode())
    DENOMINAZIONE = Column(Unicode())
    SEDE = Column(Unicode())
    CODICE_FISCALE = Column(Unicode())


class Titolarita_MM(Base):
    __tablename__ = 'catasto_titolarita_mm'

    particella_id = Column(Integer, ForeignKey('catasto_particelle.id'), primary_key=True)
    soggetto_id = Column(Integer, ForeignKey('catasto_soggetti.id'), primary_key=True)


def upload_censuario(dns, censuario):
    Base.metadata.bind = dns

    soggetti_table = Soggetti.__table__
    CODICE_COMUNE =censuario['CODICE_COMUNE']

    for soggetto_id, soggetto in censuario['SOGGETTI'].items():
        IDENTIFICATIVO_SOGGETTO, TIPO_SOGGETTO = soggetto_id
        if TIPO_SOGGETTO not in ['G']:
            continue
        print soggetto
        sogg = soggetti_table.select().where(
            soggetti_table.c.CODICE_COMUNE==IDENTIFICATIVO_SOGGETTO
        ).where(
            soggetti_table.c.IDENTIFICATIVO_SOGGETTO==IDENTIFICATIVO_SOGGETTO
        ).where(
            soggetti_table.c.TIPO_SOGGETTO==TIPO_SOGGETTO
        ).execute().fetchall()

        if len(sogg) > 1:
            print 'duplicate sogg!'
        elif len(sogg) == 1:
            print 'update', sogg[0].IDENTIFICATIVO_SOGGETTO, IDENTIFICATIVO_SOGGETTO
            sogg_id = sogg[0].id
            soggetti_table.update().where(soggetti_table.c.id==sogg_id).values(**soggetto).execute()
        else:
            print 'insert', IDENTIFICATIVO_SOGGETTO
            result = soggetti_table.insert().values(**soggetto).execute()
            sogg_id = result.last_inserted_ids()[0]

        print sogg_id

        particella_table = Particella.__table__

        # for tit in censuario['TITOLARITA']:
        #     T_IDENTIFICATIVO_SOGGETTO, T_TIPO_SOGGETTO, IDENTIFICATIVO_IMMOBILE, TIPO_IMMOBILE = tit
        #     if (T_IDENTIFICATIVO_SOGGETTO, T_TIPO_SOGGETTO) != (IDENTIFICATIVO_SOGGETTO, TIPO_SOGGETTO):
        #         continue
            
        #     if TIPO_IMMOBILE == 'T':
        #         immobile = censuario['TERRENI'][IDENTIFICATIVO_IMMOBILE]
        #     elif TIPO_IMMOBILE == 'F':
        #         immobile = censuario['FABBRICATI'][IDENTIFICATIVO_IMMOBILE]

        #     part = particella_table.select().where(
        #         particella_table.c.comune==CODICE_COMUNE
        #     ).where(
        #         particella_table.c.foglio=='%s_%s00' % (CODICE_COMUNE, ('000' + terreno['FOGLIO'])[-4:])
        #     ).where(
        #         particella_table.c.particella==terreno['NUMERO'].lstrip('0')
        #     ).execute().fetchall()
        #     if len(part) > 1:
        #         print 'duplicate terreno!'
        #     elif len(part) == 1:
        #         Titolarita_MM.__table__.delete().where(Titolarita_MM.__table__.c.soggetto_id==sogg_id).where(Titolarita_MM.__table__.c.particella_id==part[0].id).execute()
        #         Titolarita_MM.__table__.insert().values(soggetto_id=sogg_id, particella_id=part[0].id).execute()
        #     else:
        #         print 'missing!', terreno
