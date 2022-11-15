import functools
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=('GET', 'POST'))
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

                flash(f"Created account {columbia_uni}", category="success")

            except Exception as e:
                error = f"User {columbia_uni} is already registered."
                flash(error, category="error")
                return redirect(url_for("auth.register"))

            return redirect(url_for("auth.login"))

    elif request.method == 'GET':
        return render_template('auth/register.html')


@auth.route('/login', methods=('GET', 'POST'))
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
            session['major'] = user['major']
            session['listing_access'] = user['has_job_listings_access']
            session['deactivated'] = user['is_deactivated']
            session['is_admin'] = user['is_admin']
            flash("Logged in Successfully!", category="success")
            return redirect(url_for('user.jobPosting'))
        else:
            flash(error, category="error")
            return render_template('auth/login.html')

    elif request.method == 'GET':
        return render_template('auth/login.html')


@auth.before_app_request
def load_logged_in_user():
    columbia_uni = session.get('columbia_uni')

    if columbia_uni is None:
        g.user = None
    else:
        g.user = g.conn.execute(
            'SELECT * FROM users WHERE columbia_uni = %s', [columbia_uni,]
        ).fetchone()


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
