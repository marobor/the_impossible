from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
from flask_security import roles_required
from werkzeug.utils import secure_filename

import os

from . import db
from .models import Post

views = Blueprint("views", __name__)


@views.route("/home")
def home():
    return render_template("index.html", user=current_user)


@views.route("/")
def intro():
    print(current_app.config['UPLOAD_FOLDER'])
    return render_template("intro.html", user=current_user)


@views.route('/profile')
def profile():
    return "<h1>PROFILE</h1>"


@views.route('/admin-console')
@login_required
@roles_required('admin')
def admin_console():
    return render_template("admin_console.html", user=current_user)


@views.route('/<slug>')
def show_post(slug):
    post = Post.query.filter(Post.slug == slug).first()
    return render_template('posts/post.html', post=post, user=current_user)


@views.route('/create-post', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_post():
    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("ckeditor")
        file = request.files['file']

        # TODO: Default image if video not provided
        if not title or not content:
            flash('Please fill in all the fields.', category='error')
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_post = Post(title=title, content=content, image=filename)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!', category='success')

    return render_template("posts/create_post.html", user=current_user)


# TODO: post dratf?
