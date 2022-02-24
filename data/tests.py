import os
import unittest

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import Service, Vuln, Exploit
from models import create_tables, get_db_engine, get_db_session, close_db
import settings


class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.eng = get_db_engine(test=True)
        create_tables(cls.eng)
        with open(settings.TEST_DATA_FILE, 'r') as raw_sql:
            for line in raw_sql.readlines():
                safe_sql = sqlalchemy.text(line)
                cls.eng.execute(safe_sql)
        cls.session = get_db_session(cls.eng)

    @classmethod
    def tearDownClass(cls):
        close_db(cls.session, cls.eng)
        os.remove(settings.DATABASE['test'])
        return super().tearDownClass()

    def test_services_loaded(self):
        services = self.session.query(Service).all()
        self.assertEqual(len(services), 3)
    
    def test_vulns_loaded(self):
        vulns = self.session.query(Vuln).all()
        self.assertEqual(len(vulns), 2)
    
    def test_exploits_loaded(self):
        exploits = self.session.query(Exploit).all()
        self.assertEqual(len(exploits), 1)
    
    def test_relationships(self):
        vuln = self.session.query(Vuln).get(2)
        self.assertEqual(vuln.service.id, 2)
        self.assertEqual(len(vuln.exploits), 1)

        vuln = self.session.query(Vuln).get(1)
        self.assertEqual(vuln.service.id, 1)
        self.assertEqual(len(vuln.exploits), 0)
