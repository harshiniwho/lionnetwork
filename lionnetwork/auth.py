import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        columbia_uni = request.form['columbia_uni']
        password = request.form['password']
        name = request.form['name']
        major = request.form['major']

        error = None

        if not columbia_uni:
            error = 'Columbia UNI is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                if name != None and major != None:
                    g.conn.execute(
                        "INSERT INTO users (columbia_uni, password, name, major) VALUES (%s, %s, %s, %s)",
                        [columbia_uni, generate_password_hash(password), name, major],
                    )
                elif name != None:
                    g.conn.execute(
                        "INSERT INTO users (columbia_uni, password, name) VALUES (%s, %s, %s)",
                        [columbia_uni, generate_password_hash(password), name],
                    )
                elif major != None:
                    g.conn.execute(
                        "INSERT INTO users (columbia_uni, password, major) VALUES (%s, %s, %s)",
                        [columbia_uni, generate_password_hash(password), major],
                    )
                else:
                    g.conn.execute(
                        "INSERT INTO users (columbia_uni, password) VALUES (%s, %s)",
                        [columbia_uni, generate_password_hash(password)],
                    )
            except Exception as e:
                error = f"User {columbia_uni} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        columbia_uni = request.form['columbia_uni']
        password = request.form['password']
        error = None
        user = g.conn.execute(
            'SELECT * FROM users WHERE columbia_uni = %s', [columbia_uni,]
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['columbia_uni'] = user['columbia_uni']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    columbia_uni = session.get('columbia_uni')

    if columbia_uni is None:
        g.user = None
    else:
        g.user = g.conn.execute(
            'SELECT * FROM users WHERE columbia_uni = %s', [columbia_uni,]
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
