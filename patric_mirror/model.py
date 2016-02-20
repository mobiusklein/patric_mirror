from sqlalchemy.ext.declarative import declarative_base


from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import (PickleType, Numeric, String,
                        Column, Integer, ForeignKey, Text)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def simple_repr(self):  # pragma: no cover
    template = "{self.__class__.__name__}({d})"
    items = [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]
    parts = []
    for key, value in items:
        parts.append("%s=%r" % (key, value))

    return template.format(self=self, d=', '.join(parts))

Base.__repr__ = simple_repr


class Genome(Base):
    __tablename__ = "Genome"

    accession = Column(String(56), primary_key=True)
    genome_name = Column(String(128), index=True)
    genome_id = Column(String(12), index=True)

    taxonomy_id = Column(Integer, index=True)


class Feature(Base):
    __tablename__ = "Feature"

    accession = Column(String(56), ForeignKey(Genome.accession), index=True)
    patric_id = Column(String(56), primary_key=True)
    annotation = Column(String(56), index=True)

    refseq_locus_tag = Column(String(56), index=True)
    alt_locus_tag = Column(String(56), index=True)

    uniprotkb_accession = Column(String(56), index=True)

    feature_type = Column(String(56), index=True)
    genome = relationship(Genome, backref=backref('features', lazy='dynamic'))

    start = Column(Integer, index=True)
    end = Column(Integer, index=True)

    strand = Column(String(3), index=True)
    na_length = Column(Integer)
    gene = Column(String(56), index=True)
    product = Column(String(56), index=True)
    figfam_id = Column(String(56), index=True)
    plfam_id = Column(String(56), index=True)
    pgfam_id = Column(String(56), index=True)

    @hybrid_method
    def spans(self, point):
        return (self.start <= point) & (point < self.end)


class GOTerm(Base):
    __tablename__ = "GOTerm"

    id = Column(Integer, primary_key=True)
    feature_id = Column(String(56), ForeignKey(Feature.patric_id), index=True)
    go_id = Column(String(56), index=True)
    description = Column(String(128), index=True)

    feature = relationship(Feature, backref=backref("go_terms"))


class Pathway(Base):
    __tablename__ = "Pathway"

    id = Column(Integer, primary_key=True)
    feature_id = Column(String(56), ForeignKey(Feature.patric_id), index=True)
    pathway_id = Column(String(56), index=True)
    description = Column(String(128), index=True)

    feature = relationship(Feature, backref=backref("pathways"))


class EnzymeCode(Base):
    __tablename__ = "EnzymeCode"

    id = Column(Integer, primary_key=True)
    feature_id = Column(String(56), ForeignKey(Feature.patric_id), index=True)
    enzyme_id = Column(String(56), index=True)
    description = Column(String(128), index=True)

    feature = relationship(Feature, backref=backref("enzymes"))


def make_sqlite_uri(path):
    return "sqlite:///%s" % path


def connect(path):
    engine = create_engine(make_sqlite_uri(path))
    return engine


def initialize(path):
    eng = connect(path)
    Base.metadata.create_all(bind=eng)
    return eng


def make_session(path):
    eng = connect(path)
    return sessionmaker(bind=eng)()
