from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from lionnetwork.auth import login_required

forums = Blueprint('forums', __name__, url_prefix='/forums')

@forums.route('/')
def index():
    forums = g.conn.execute(
        'SELECT *'
        ' FROM forums'
        ' ORDER BY forum_name'
    ).fetchall()
    session['forum_id'] = ""
    return render_template('forums/index.html', forums=forums)


@forums.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None

        if not name:
            error = 'Forum name is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'INSERT INTO forums (forum_name, forum_description, columbia_uni)'
                ' VALUES (%s, %s, %s)',
                [name, description, g.user['columbia_uni']]
            )
            return redirect(url_for('forums.index'))

    return render_template('forums/create.html')


def get_forum(id, check_admin=True):
    forum = g.conn.execute(
        'SELECT *'
        ' FROM forums'
        ' WHERE forum_id = %s',
        [id,]
    ).fetchone()

    if forum is None:
        abort(404, f"Forum id {id} doesn't exist.")

    #TODO modify below check condition for checking if user is admin
    # if !check_admin:
    #     abort(403)

    return forum


@forums.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    forum = get_forum(id)

    if request.method == 'POST':
        name = request.form['forum_name']
        description = request.form['forum_description']
        error = None

        if not name:
            error = 'Forum name is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'UPDATE forums SET forum_name = %s, forum_description = %s'
                ' WHERE forum_id = %s',
                (name, description, id)
            )
            return redirect(url_for('forums.index'))

    return render_template('forums/update.html', forum=forum)


@forums.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_forum(id)
    # enabled cascaded deletes for comments and posts
    g.conn.execute('DELETE FROM forums WHERE forum_id = %s', (id,))
    return redirect(url_for('forums.index'))
