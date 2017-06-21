import os
import tempfile

from flask_bcrypt import Bcrypt

import sqlite3

DATABASE = os.path.join(tempfile.gettempdir(), 'alayatodo.db')


def main():
    bcrypt = Bcrypt()

    with sqlite3.connect(DATABASE) as db:
        cur = db.execute(
            'SELECT id, password FROM users'
        )

        for row in cur.fetchall():
            password_hash = bcrypt.generate_password_hash(row[1])
            user_id = row[0]

            cur.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (password_hash, user_id)
            )


if __name__ == '__main__':
    main()

