import unittest
import sqlite3
import os
import tempfile

import alayatodo


class TodoTest(unittest.TestCase):
    def setUp(self):
        alayatodo.app.testing = True
        self.app = alayatodo.app.test_client()

        alayatodo.app.config['DATABASE'] = os.path.join(tempfile.gettempdir(), 'alayatodo.test.db')
        self._build_database()

    def tearDown(self):
        os.remove(alayatodo.app.config['DATABASE'])

    @staticmethod
    def _build_database():
        with open('../resources/database.sql') as f, sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            sql_script = f.read()
            db.executescript(sql_script)

    def _log_in(self):
        with self.app.session_transaction() as session:
            session['logged_in'] = True
            session['user'] = {'id': '1'}

    def test_todos_post_empty_description(self):
        """
        POSTing a TODO with an empty description generates a flash message.
        """

        self._log_in()

        response = self.app.post('/todo/', follow_redirects=True)

        self.assertTrue(
            '<div class="flashed-message">TODO items must have a description. Please try again.</div>' in response.data
        )

    def test_todos_post_valid_description_displays_in_ui(self):
        """
        POSTing a TODO with a valid description properly displays it in the user interface.
        """

        self._log_in()

        response = self.app.post('/todo/', data={'description': 'Buy Apples'}, follow_redirects=True)

        self.assertTrue('Buy Apples' in response.data)
