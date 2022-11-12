from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session,
)
from werkzeug.exceptions import abort

from lionnetwork.auth import login_required

posts = Blueprint('posts', __name__, url_prefix='/posts')

def get_forum(id):
    forum = g.conn.execute(
        'SELECT *'
        ' FROM forums'
        ' WHERE forum_id = %s',
        [id,]
    ).fetchone()

    if forum is None:
        abort(404, f"Forum id {id} doesn't exist.")

    return forum['forum_name']

@posts.route('/<int:id>', methods=('GET',))
@login_required
def index(id):
    forum_name = get_forum(id)
    session['forum_id'] = id
    posts = g.conn.execute('SELECT p.post_id, p.post_text, p.timestamp_posted, p.columbia_uni, f.forum_id, f.forum_name FROM posts p JOIN forums f on p.forum_id = f.forum_id WHERE f.forum_id = %s', (id,)).fetchall()
    
    return render_template('posts/index.html', posts=posts, forum_name=forum_name)


@posts.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        post_text = request.form['post_text']
        post_id = request.form['post_id']
        forum_id = session['forum_id']
        if forum_id == None:
            flash("Invalid state!")
            return redirect(url_for('forums.index'))
        error = None

        if not post_text:
            error = 'Post text is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'INSERT INTO posts (post_id, forum_id, post_text, columbia_uni, timestamp_posted)'
                ' VALUES (%s, %s, %s, %s)',
                [post_id, forum_id, post_text, g.user['columbia_uni'], ]
            )
            return redirect(url_for('posts.index', id=session['forum_id']))

    return render_template('posts/create.html')

def get_post(id):
    post = g.conn.execute(
        'SELECT *'
        ' FROM posts'
        ' WHERE post_id = %s',
        [id,]
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post


@posts.route('/view/<int:id>', methods=('GET',))
def show(id):
    print("in here?")
    post = get_post(id)
    comments = g.conn.execute(
        'SELECT c.comment_text, c.timestamp_posted, c.columbia_uni as poster FROM comments c JOIN posts p on c.post_id = p.post_id and c.forum_id = p.forum_id WHERE p.post_id = %s and p.forum_id = %s', (id, session['forum_id'])
    ).fetchall()
    return render_template('posts/show.html', post=post, comments=comments)


@posts.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
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
            return redirect(url_for('posts.index', id=session['forum_id']))
    return render_template('posts/update.html', post=post)


@posts.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # enabled cascade deletes for comments
    g.conn.execute('DELETE FROM posts WHERE post_id = %s', (id,))
    return redirect(url_for('posts.index', id=session['forum_id']))
