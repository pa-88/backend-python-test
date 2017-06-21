import os
import tempfile
import unittest
from abc import ABCMeta

import sqlite3

import alayatodo
from resources import password_hash_data_migration


class AbstractTodoTestCase(unittest.TestCase):
    __metaclass__ = ABCMeta

    def setUp(self):
        alayatodo.app.testing = True
        self.app = alayatodo.app.test_client()

        alayatodo.app.config['DATABASE'] = os.path.join(tempfile.gettempdir(), 'alayatodo.test.db')
        self._build_database()

    def tearDown(self):
        os.remove(alayatodo.app.config['DATABASE'])

    @staticmethod
    def _build_database():
        scripts = [
            '../resources/database.sql',
            '../resources/fixtures.sql',
            '../resources/add_completed_field.sql'
        ]

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            for script in scripts:
                with open(script) as f:
                    sql_script = f.read()
                    db.executescript(sql_script)

        password_hash_data_migration.main()

    def _log_in(self):
        with self.app.session_transaction() as session:
            session['logged_in'] = True
            session['user'] = {'id': '1'}
