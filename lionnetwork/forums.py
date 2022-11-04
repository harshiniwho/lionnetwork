from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lionnetwork.auth import login_required

bp = Blueprint('forums', __name__, url_prefix='/forums')

@bp.route('/')
def index():
    forums = g.conn.execute(
        'SELECT *'
        ' FROM forums'
        ' ORDER BY forum_name'
    ).fetchall()
    return render_template('forums/index.html', forums=forums)


@bp.route('/create', methods=('GET', 'POST'))
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
                'INSERT INTO forums (forum_name, description, columbia_uni)'
                ' VALUES (%s, %s, %s)',
                [name, description, g.user['id']]
            )
            return redirect(url_for('forums.index'))

    return render_template('forums/create.html')


def get_forum(id, check_author=True):
    forum = g.conn.execute(
        'SELECT *'
        ' FROM forums'
        ' WHERE forum_id = %s',
        [id,]
    ).fetchone()

    if forum is None:
        abort(404, f"Forum id {id} doesn't exist.")

    #TODO modify below check condition for checking if user is admin
    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return forum


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
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
                'UPDATE forums SET forum_name = %s, description = %s'
                ' WHERE forum_id = %s',
                (name, description, id)
            )
            return redirect(url_for('forums.index'))

    return render_template('forums/update.html', forum=forum)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_forum(id)
    g.conn.execute('DELETE FROM forums WHERE forum_id = %s', (id,))
    return redirect(url_for('forums.index'))