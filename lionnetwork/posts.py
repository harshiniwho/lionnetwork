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
    posts = g.conn.execute("SELECT p.post_id, p.post_text, to_char(timestamp_posted, 'Day DD Mon YYYY') as timestamp_posted, p.columbia_uni, f.forum_id, f.forum_name FROM posts p JOIN forums f on p.forum_id = f.forum_id WHERE f.forum_id = %s", (id,)).fetchall()
    
    return render_template('posts/index.html', posts=posts, forum_name=forum_name)


@posts.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        post_text = request.form['post_text']
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
                'INSERT INTO posts (forum_id, post_text, columbia_uni)'
                ' VALUES (%s, %s, %s)',
                [forum_id, post_text, g.user['columbia_uni'], ]
            )
            return redirect(url_for('posts.index', id=session['forum_id']))

    return render_template('posts/create.html')


def get_post(id):
    post = g.conn.execute(
        "SELECT post_id, forum_id, post_text, to_char(timestamp_posted, 'Day DD Mon YYYY') as timestamp_posted, p.columbia_uni, u.name"
        ' FROM posts p JOIN users u ON p.columbia_uni = u.columbia_uni'
        ' WHERE post_id = %s',
        [id,]
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post


def get_comment(id):
    comment = g.conn.execute(
        'SELECT *'
        ' FROM comments'
        ' WHERE comment_id = %s',
        [id,]
    ).fetchone()

    if comment is None:
        abort(404, f"Comment id {id} doesn't exist.")

    return comment


@posts.route('/view/<int:id>', methods=('GET',))
def show(id):
    post = get_post(id)
    comments = g.conn.execute(
        "SELECT c.comment_id, c.comment_text, to_char(c.timestamp_posted, 'Day DD Mon YYYY') as timestamp_posted, c.columbia_uni as poster, u.name as name FROM comments c JOIN posts p on c.post_id = p.post_id and c.forum_id = p.forum_id JOIN users u on c.columbia_uni = u.columbia_uni WHERE p.post_id = %s and p.forum_id = %s", (id, session['forum_id'])
    ).fetchall()
    return render_template('posts/show.html', post=post, comments=comments)


@posts.route('/<int:id>/comment', methods=('POST',))
@login_required
def comment(id):
    comment_text = request.form['comment_text']
    g.conn.execute(
        'INSERT INTO comments (forum_id, post_id, comment_text, columbia_uni)'
        ' VALUES (%s, %s, %s, %s)',
        [session["forum_id"], id, comment_text, g.user['columbia_uni'], ]
    )
    return redirect(url_for('posts.show', id=id))


@posts.route('/<int:id>/comment/delete', methods=('POST',))
@login_required
def comment_delete(id):
    print("in here?")
    comment = get_comment(id)
    g.conn.execute('DELETE FROM comments WHERE comment_id = %s', (id,))
    return redirect(url_for('posts.show', id=comment['post_id']))


@posts.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        post_text = request.form['post_text']
        error = None

        if not post_text:
            error = 'Post text is required.'

        if error is not None:
            flash(error)
        else:
            g.conn.execute(
                'UPDATE posts SET post_text = %s'
                ' WHERE post_id = %s AND forum_id = %s',
                (post_text, id, session['forum_id'])
            )
            return redirect(url_for('posts.index', id=session['forum_id']))
    return render_template('posts/update.html', post=post)


@posts.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # enabled cascade deletes for comments
    g.conn.execute('DELETE FROM posts WHERE post_id = %s', (id,))
    return redirect(url_for('posts.index', id=session['forum_id']))
