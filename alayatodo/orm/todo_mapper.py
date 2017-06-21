from flask import g

from alayatodo.entities.todo import Todo
from alayatodo.orm import user_mapper


def _todo_row_factory(cursor, row):
    result = {}

    for i, col in enumerate(cursor.description):
        # col is a 6tuple where the first field is the column name.
        result[col[0]] = row[i]

    return Todo(result['id'], user_mapper.get_user_by_id(result['user_id']), result['description'], result['completed'])


def get_todo_by_id(todo_id, user_id):
    sql = 'SELECT * FROM todos WHERE id = ? AND user_id = ?'

    g.db.row_factory = _todo_row_factory

    cur = g.db.execute(sql, (todo_id, user_id))

    return cur.fetchone()


def get_number_of_todos_for_user(user_id):
    sql = "SELECT COUNT(*) FROM todos WHERE user_id = ?"

    cur = g.db.execute(sql, (user_id,))

    return cur.fetchone()['COUNT(*)']


def get_page_of_todos(user_id, page_size, min_item):
    sql = "SELECT * FROM todos WHERE user_id = ? LIMIT ? OFFSET ?"

    g.db.row_factory = _todo_row_factory

    cur = g.db.execute(sql, (user_id, page_size, min_item))

    return cur.fetchall()


def create_todo(todo):
    sql = "INSERT INTO todos (user_id, description, completed) VALUES (?, ?, ?)"

    g.db.execute(sql, (todo.user.id, todo.description, todo.completed))

    g.db.commit()


def delete_todo(todo):
    sql = "DELETE FROM todos WHERE id = ? AND user_id = ?"

    cursor = g.db.execute(sql, (todo.id, todo.user.id))

    g.db.commit()

    return cursor.rowcount


def update_completion_status(todo):
    sql = "UPDATE todos SET completed = ? WHERE id = ? AND user_id = ?"

    g.db.execute(sql, (todo.completed, todo.id, todo.user.id))

    g.db.commit()
