import decorator
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash
)

from alayatodo import app, bcrypt


@decorator.decorator
def protected_route(fn, *args):
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        # * explodes the tuple.
        return fn(*args)


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
@protected_route
def todo(id):
    user_id = session['user']['id']

    cur = g.db.execute(
        "SELECT * FROM todos WHERE id = ? AND user_id = ?",
        (id, user_id)
    )

    todo = cur.fetchone()

    if todo:
        return render_template('todo.html', todo=todo)
    else:
        flash('You may only view TODOs which belong to you.', 'error')
        return redirect('/todo')


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@protected_route
def todos():
    user_id = session['user']['id']

    cur = g.db.execute(
        "SELECT * FROM todos WHERE user_id = ?",
        (user_id,)
    )

    todos = cur.fetchall()
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
