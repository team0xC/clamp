from sqlalchemy import Table, ForeignKey, BLOB, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, backref, relationship


Base = declarative_base()


service_exploit = Table(
    "service_explot",
    Base.medatata,
    Column("service_id", Integer, ForeignKey("services.id")),
    Column("exploit_id", Integer, ForeignKey("exploits.id"))
)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    port = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Service (name='{self.name}', port='{self.port}'>"


class Vuln(Base):
    __tablename__ = "vulns"

    id = Column(Integer, primary_key=True)
    service = relationship("Service", backref=backref("vuln"))
    benign = Column(Boolean, server_default=False)
    patched = Column(Boolean, server_default=False)
    sequence = Column(BLOB, nullable=False)

    def __repr__(self):
        return f"<Vuln (id='{self.id}', service='{self.service}', patched='{self.patched}', benign='{self.benign}'>"


class Exploit(Base):
    __tablename__ = "exploits"

    id = Column(Integer, primary_key=True)
    service = relationship("Vuln", backref=backref("exploit"))
    service = relationship("Service", secondary=service_exploit, backref=backref("exploits"))
    path = Column(String, nullable=False)
    flag_ct_rd = Column(Integer, server_default=0)
    flag_ct_cum = Column(Integer, server_default=0)
