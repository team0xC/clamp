from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

import settings


Base = declarative_base()


def get_db_engine(test=False):
    instance = 'test' if test==True else 'prod'
    return create_engine(f"sqlite:///{settings.DATABASE[instance]}")


def get_db_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def close_db(session, engine):
    session.close()
    engine.dispose()


def create_tables(engine):
    Base.metadata.create_all(engine)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    port = Column(Integer, nullable=False)

    vulns = relationship("Vuln", back_populates="service")
    exploits = relationship("Exploit", back_populates="service")

    def __repr__(self):
        return f"<Service (name='{self.name}', port='{self.port}')>"


class Vuln(Base):
    __tablename__ = "vulns"

    id = Column(Integer, primary_key=True)
    benign = Column(Boolean, default=False)
    patched = Column(Boolean, default=False)
    sequence = Column(String, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    service = relationship("Service", back_populates="vulns")
    exploits = relationship("Exploit", back_populates="vuln")

    def __repr__(self):
        return f"<Vuln (id='{self.id}', service='{self.service.name}')>"


class Exploit(Base):
    __tablename__ = "exploits"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    flag_ct_rd = Column(Integer, default=0)
    flag_ct_cum = Column(Integer, default=0)
    vuln_id = Column(Integer, ForeignKey("vulns.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    service = relationship("Service", back_populates="exploits")
    vuln = relationship("Vuln", back_populates="exploits")

    def name(self):
        return self.path.split('/')[-1]

    def __repr__(self):
        return f"<Exploit (id='{self.id}', service='{self.service.name}', name='{self.name()}')>"
