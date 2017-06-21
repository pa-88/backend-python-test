import json

from bs4 import BeautifulSoup

from tests.abstract_todo_test_case import AbstractTodoTestCase


class TodoUITest(AbstractTodoTestCase):

    def test_todos_post_empty_description_displays_flash_message(self):
        """
        POSTing a TODO with an empty description generates a flash message.
        """

        self._log_in()

        response = self.app.post('/todo/', follow_redirects=True)

        self.assertTrue(
            '<div class="flashed-message">TODO items must have a non-empty description. Please try again.</div>' in response.data
        )

    def test_todos_post_whitespace_only_description_displays_flash_message(self):
        """
        POSTing a TODO with only whitespace in the description generates a flash message.
        """

        self._log_in()

        response = self.app.post('/todo/', data={'description': '    '}, follow_redirects=True)

        self.assertTrue(
            '<div class="flashed-message">TODO items must have a non-empty description. Please try again.</div>' in response.data
        )

    def test_todos_post_valid_description_displays_in_ui(self):
        """
        POSTing a TODO with a valid description properly displays it in the user interface.
        """

        self._log_in()

        response = self.app.post('/todo/', data={'description': 'Buy Apples'}, follow_redirects=True)

        self.assertTrue('Buy Apples' in response.data)

    def test_todos_get_by_valid_id_properly_displays_item_in_ui(self):
        """
        GETting a TODO by a valid id displays it properly in the UI.
        """

        self._log_in()

        response = self.app.get('/todo/2')

        # Parse the html to find the table contents.
        soup = BeautifulSoup(response.data, 'html.parser')
        table_data = soup.find_all('td')

        self.assertEqual(table_data[2].string, 'lorem ac odio')

    def test_todos_get_properly_displays_all_items_in_ui(self):
        """
        GETting the TODO collection displays all TODOs properly in the UI.
        """

        expected_todos = [
            'Vivamus tempus',
            'lorem ac odio',
            'Ut congue odio',
            'Sodales finibus',
            'Accumsan nunc vitae'
        ]

        self._log_in()

        response = self.app.get('/todo/')

        soup = BeautifulSoup(response.data, 'html.parser')

        # Find all links within table data.
        todos = [a.string.strip() for a in soup.find('table').find_all('a')]

        self.assertEqual(todos, expected_todos)

    def test_todos_delete_properly_removes_a_valid_todo_from_ui(self):
        """
        Deleting an item properly removes it from the UI.
        """

        self._log_in()

        response = self.app.post('/todo/1', follow_redirects=True)

        self.assertTrue('Vivamus tempus' not in response.data)

    def test_user_cannot_view_another_users_todo(self):
        """
        GETting todo/<id> for a TODO which belongs to another user will results in a flash
        message indicating that the user cannot view it.
        """

        self._log_in()

        response = self.app.get('/todo/6', follow_redirects=True)

        self.assertTrue(
            '<div class="flashed-message">You may only view TODOs which belong to you.</div>' in response.data
        )

    def test_user_can_request_all_todos_as_json(self):
        """
        The user can request the entire todo collection as JSON.
        """

        self._log_in()

        expected_response = [
            {
                'id': 1,
                'user_id': 1,
                'completed': 0,
                'description': 'Vivamus tempus'
            },
            {
                'id': 2,
                'user_id': 1,
                'completed': 0,
                'description': 'lorem ac odio'
            },
            {
                'id': 3,
                'user_id': 1,
                'completed': 0,
                'description': 'Ut congue odio'
            },
            {
                'id': 4,
                'user_id': 1,
                'completed': 0,
                'description': 'Sodales finibus'
            },
            {
                'id': 5,
                'user_id': 1,
                'completed': 0,
                'description': 'Accumsan nunc vitae'
            }
        ]

        response = self.app.get('/todo/json', follow_redirects=True)

        data = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(expected_response, data)

    def test_user_can_request_a_single_todo_as_json(self):
        """
        The user can request a todo as JSON.
        """

        self._log_in()

        expected_response = {
            'id': 1,
            'user_id': 1,
            'completed': 0,
            'description': 'Vivamus tempus'
        }

        response = self.app.get('/todo/1/json', follow_redirects=True)

        data = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(expected_response, data)

    def test_requesting_an_invalid_todo_as_json_returns_empty_object(self):
        """
        When requesting an invalid todo as json, an empty object is returned.
        """

        self._log_in()

        expected_response = {}

        response = self.app.get('/todo/100/json', follow_redirects=True)

        data = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(expected_response, data)
