import decorator
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify)

from alayatodo import app, bcrypt


@decorator.decorator
def protected_route(fn, *args):
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        # * explodes the tuple.
        return fn(*args)


def todo_row_factory(cursor, row):
    result = {}

    for i, col in enumerate(cursor.description):
        # col is a 6tuple where the first field is the column name.
        result[col[0]] = row[i]

    return result


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = ?"
    cur = g.db.execute(sql, (username,))
    user = cur.fetchone()
    if user and bcrypt.check_password_hash(user[2], password):
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@app.route('/todo/<id>/json', methods=['GET'])
@protected_route
def todo(id):
    user_id = session['user']['id']
    path = request.path

    g.db.row_factory = todo_row_factory

    cur = g.db.execute(
        "SELECT * FROM todos WHERE id = ? AND user_id = ?",
        (id, user_id)
    )

    todo = cur.fetchone()

    if todo:
        if path.endswith('json'):
            return jsonify(todo)
        else:
            return render_template('todo.html', todo=todo)
    else:
        if path.endswith('json'):
            return jsonify({})
        else:
            flash('You may only view TODOs which belong to you.', 'error')
            return redirect('/todo')


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@app.route('/todo/json', methods=['GET'])
@protected_route
def todos():
    user_id = session['user']['id']
    path = request.path

    g.db.row_factory = todo_row_factory

    cur = g.db.execute(
        "SELECT * FROM todos WHERE user_id = ?",
        (user_id,)
    )

    todos = cur.fetchall()

    if path == '/todo/json':
        return jsonify(todos)
    else:
        return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@protected_route
def todos_POST():
    description = request.form.get('description', '').strip()

    if not description:
        flash('TODO items must have a non-empty description. Please try again.', 'error')
        return redirect('/todo')

    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES (?, ?)",
        (session['user']['id'], request.form.get('description', ''))
    )
    g.db.commit()

    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@protected_route
def todo_delete(id):
    user_id = session['user']['id']

    g.db.execute(
        "DELETE FROM todos WHERE id = ? AND user_id = ?",
        (id, user_id))
    g.db.commit()

    return redirect('/todo')


@app.route('/todo/toggle/<id>', methods=['POST'])
@protected_route
def todo_toggle_complete(id):
    user_id = session['user']['id']

    completed = not int(request.form.get('completed', ''))
    origin = request.form.get('origin', '/todo')

    g.db.execute(
        "UPDATE todos SET completed = ? WHERE id = ? AND user_id = ?",
        (completed, id, user_id)
    )
    g.db.commit()

    return redirect(origin)
