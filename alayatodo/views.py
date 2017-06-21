from math import ceil

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
from alayatodo.entities.todo import Todo
from alayatodo.orm import user_mapper, todo_mapper


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

    user = user_mapper.get_user_by_username(username)

    if user and bcrypt.check_password_hash(user.password, password):
        session['user'] = user.__dict__
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>', methods=['GET'])
@protected_route
def todo(id):
    user_id = session['user']['id']
    path = request.path

    todo = todo_mapper.get_todo_by_id(id, user_id)

    if todo:
        if path.endswith('json'):
            return jsonify(todo.to_json())
        else:
            return render_template('todo.html', todo=todo)
    else:
        if path.endswith('json'):
            return jsonify({})
        else:
            flash('You may only view TODOs which belong to you.', 'error')
            return redirect('/todo')


@app.route('/todo/json/', methods=['GET'])
@app.route('/todo/json', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@app.route('/todo', methods=['GET'])
@protected_route
def todos():
    user_id = session['user']['id']
    path = request.path

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    g.db.row_factory = todo_row_factory

    total_items = todo_mapper.get_number_of_todos_for_user(user_id)

    max_page = int(ceil(total_items / float(page_size)))

    if page < 1 or page > max_page:
        page = 1

    min_item = ((page - 1) * page_size)

    todos = todo_mapper.get_page_of_todos(user_id, page_size, min_item)

    if path.startswith('/todo/json'):
        return jsonify([td.to_json() for td in todos])
    else:
        return render_template('todos.html', page=page, todos=todos, max_page=max_page, page_size=page_size)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@protected_route
def todos_POST():
    description = request.form.get('description', '').strip()

    if not description:
        flash('TODO items must have a non-empty description. Please try again.', 'error')
        return redirect('/todo')

    user = user_mapper.get_user_by_id(session['user']['id'])
    todo = Todo(None, user, request.form.get('description', ''), False)

    todo_mapper.create_todo(todo)

    flash('Your TODO has been added.', 'confirmation')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@protected_route
def todo_delete(id):
    user_id = session['user']['id']

    todo = todo_mapper.get_todo_by_id(id, user_id)

    if todo:
        row_count = todo_mapper.delete_todo(todo)

        if row_count == 1:
            flash('Your TODO has been deleted.', 'confirmation')

    return redirect('/todo')


@app.route('/todo/toggle/<id>', methods=['POST'])
@protected_route
def todo_toggle_complete(id):
    user_id = session['user']['id']
    origin = request.form.get('origin', '/todo')

    todo = todo_mapper.get_todo_by_id(id, user_id)
    todo.completed = not todo.completed

    todo_mapper.update_completion_status(todo)

    return redirect(origin)
