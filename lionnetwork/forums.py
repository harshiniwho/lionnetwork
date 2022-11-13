from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from lionnetwork.auth import login_required

forums = Blueprint('forums', __name__, url_prefix='/forums')


def fetch_industries():
    industries = g.conn.execute(
        'select * from industries'
    ).fetchall()
    return industries


@forums.route('/')
def index():
    forums = g.conn.execute(
        'SELECT f.forum_id, f.forum_name, f.forum_description, f.columbia_uni, i.industry_name'
        ' FROM forums f join industries i on f.industry_id = i.industry_id'
        ' ORDER BY forum_name'
    ).fetchall()
    session['forum_id'] = ""
    return render_template('forums/index.html', forums=forums)


@forums.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        forum_name = request.form['forum_name']
        forum_description = request.form['forum_description']
        
        error = None

        print(forum_name)
        industry_id = request.form['industry_id']

        if not forum_name:
            error = 'Forum name is required.'
        if not industry_id:
            error = 'Industry name is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'INSERT INTO forums (forum_name, forum_description, columbia_uni, industry_id)'
                ' VALUES (%s, %s, %s, %s)',
                [forum_name, forum_description, g.user['columbia_uni'], industry_id]
            )
            return redirect(url_for('forums.index'))
    
    
    return render_template('forums/create.html', industries=fetch_industries())


def get_forum(id, check_admin=True):
    forum = g.conn.execute(
        'SELECT f.forum_id, f.forum_name, f.forum_description, f.columbia_uni, i.industry_name'
        ' FROM forums f join industries i on f.industry_id = i.industry_id'
        ' WHERE f.forum_id = %s',
        [id,]
    ).fetchone()

    if forum is None:
        abort(404, f"Forum id {id} doesn't exist.")

    return forum


@forums.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    forum = get_forum(id)

    if request.method == 'POST':
        name = request.form['forum_name']
        description = request.form['forum_description']
        industry_id = request.form['industry_id']
        error = None

        if not name:
            error = 'Forum name is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'UPDATE forums SET forum_name = %s, forum_description = %s, industry_id = %s'
                ' WHERE forum_id = %s',
                (name, description, industry_id, id)
            )
            return redirect(url_for('forums.index'))

    return render_template('forums/update.html', forum=forum, industries=fetch_industries())


@forums.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_forum(id)
    # enabled cascaded deletes for comments and posts
    g.conn.execute('DELETE FROM forums WHERE forum_id = %s', (id,))
    return redirect(url_for('forums.index'))
