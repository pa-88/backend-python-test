import sqlite3

import alayatodo
from tests.abstract_todo_test_case import AbstractTodoTestCase


class TodoDBTest(AbstractTodoTestCase):

    def test_todos_post_valid_description_properly_stores_in_db(self):
        """
        POSTing a TODO with a valid description properly stores it in the database.
        """

        self._log_in()

        self.app.post('/todo/', data={'description': 'Buy Apples'}, follow_redirects=True)

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            cur = db.execute(
                'SELECT * FROM todos WHERE user_id = ? AND description = ?',
                (1, 'Buy Apples')
            )

            row = cur.fetchone()
            cur.close()

        self.assertEqual(row, (9, 1, 'Buy Apples'))

    def test_todos_delete_properly_deletes_a_valid_todo(self):
        """
        Deleting an item properly removes it from the database.
        """

        self._log_in()

        self.app.post('/todo/1')

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            cur = db.execute(
                'SELECT * FROM todos WHERE id = 1'
            )

            row = cur.fetchone()
            cur.close()

        self.assertIsNone(row)
