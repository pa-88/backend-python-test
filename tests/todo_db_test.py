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

        self.assertEqual(row, (9, 1, 'Buy Apples', 0))

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

    def test_user_cannot_delete_another_users_todo(self):
        """
        A user cannot delete another user's TODO.
        """

        self._log_in()

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            cur = db.execute(
                'SELECT * FROM todos WHERE id = 6'
            )

            row = cur.fetchone()
            cur.close()

        self.assertIsNotNone(row)

    def test_uncompleted_task_is_toggled_to_completed(self):
        """
        Toggling the checkbox on an incomplete task will show it as completed.
        """

        self._log_in()

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            db.execute(
                'UPDATE todos SET completed = 0 WHERE id = 1'
            )

            db.commit()

            self.app.post('/todo/toggle/1', data={'completed': '0', 'origin': '/todo'}, follow_redirects=True)

            cur = db.execute(
                'SELECT * FROM todos WHERE id = 1'
            )

            row = cur.fetchone()
            cur.close()

        self.assertEquals(row[3], 1)

    def test_completed_task_is_toggled_to_incomplete(self):
        """
        Toggling the checkbox on an completed task will show it as incomplete.
        """

        self._log_in()

        with sqlite3.connect(alayatodo.app.config['DATABASE']) as db:
            db.execute(
                'UPDATE todos SET completed = 1 WHERE id = 1'
            )

            db.commit()

            self.app.post('/todo/toggle/1', data={'completed': '1', 'origin': '/todo'}, follow_redirects=True)

            cur = db.execute(
                'SELECT * FROM todos WHERE id = 1'
            )

            row = cur.fetchone()
            cur.close()

        self.assertEquals(row[3], 0)
