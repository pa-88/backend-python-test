from flask import g

from alayatodo.entities.user import User


def _user_row_factory(cursor, row):
    result = {}

    for i, col in enumerate(cursor.description):
        # col is a 6tuple where the first field is the column name.
        result[col[0]] = row[i]

    return User(result['id'], result['username'], result['password'])


def get_user_by_username(username):
    sql = "SELECT * FROM users WHERE username = ?"

    g.db.row_factory = _user_row_factory

    cur = g.db.execute(sql, (username,))

    return cur.fetchone()


def get_user_by_id(user_id):
    sql = "SELECT * FROM users WHERE id = ?"

    g.db.row_factory = _user_row_factory

    cur = g.db.execute(sql, (user_id,))

    return cur.fetchone()