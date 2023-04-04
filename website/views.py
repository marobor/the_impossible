from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for
from flask_login import login_required, current_user
from flask_security import roles_required
from werkzeug.utils import secure_filename
from datetime import datetime, date

import os

from . import db
from .models import Post, Trick, TrickVariant, UsersTricks, UserData, slugify, Category

views = Blueprint("views", __name__)


@views.route("/")
def intro():
    return render_template("intro.html", user=current_user)


@views.route("/home")
def home():
    post = Post.query.filter(Post.category_id == 2).first()
    posts = Post.query.filter(Post.category_id == 2).all()
    category = Category.query.filter(Category.id == 2).first()
    return render_template('posts/post.html', post=post, posts=posts, user=current_user, category=category.name)
    # return render_template("index.html", user=current_user)


@views.route("/about")
def about():
    post = Post.query.filter(Post.category_id == 3).first()
    posts = Post.query.filter(Post.category_id == 3).all()
    category = Category.query.filter(Category.id == 3).first()
    return render_template('posts/post.html', post=post, posts=posts, user=current_user, category=category.name)


@views.route('/profile')
@login_required
def profile():
    u_tricks = db.session.query(UsersTricks).join(Trick).join(TrickVariant).\
        filter(UsersTricks.user_id == current_user.id).order_by(UsersTricks.created_at.desc())
    user_data = UserData.query.filter(UserData.user_id == current_user.id).first()

    return render_template('user/profile.html', user=current_user, tricks=u_tricks, user_data=user_data)


@views.route('/trick/<trick_name>')
@login_required
def my_trick(trick_name):
    trick = Trick.query.filter(Trick.name == trick_name).first()
    tricks = Trick.query.all()

    # Trick variants that already been done by the current user - query result in tuples
    completed_variants = db.session.query(UsersTricks.trick_variant_id).filter_by(trick_id=trick.id,
                                                                                  user_id=current_user.id).all()
    # Tuple to int conversion
    user_variants = [int(t[0]) for t in completed_variants]

    # Content of variant list depends on trick
    if trick_name == 'Ollie':
        variants = TrickVariant.query.filter(TrickVariant.name != 'Nollie').all()
    elif trick_name == 'Nollie':
        variants = [TrickVariant.query.first()]
        print(type(variants))
    else:
        variants = TrickVariant.query.all()

    return render_template('my_tricks.html', trick=trick, tricks=tricks,
                           user=current_user, all_variants=variants, user_variants=user_variants)


def add_points(counter, trick_value):
    scale = {0: 1, 1: 1.20, 2: 2, 3: 5}
    if scale[counter]:
        points = scale[counter] * trick_value
        user_data = UserData.query.filter(UserData.user_id == current_user.id).first()
        user_data.skill_points += points
        db.session.add(user_data)
        db.session.commit()


def subtract_points(counter, trick_value):
    scale = {1: 1, 2: 1.20, 3: 2, 4: 5}
    if scale[counter]:
        points = scale[counter] * trick_value
        user_data = UserData.query.filter(UserData.user_id == current_user.id).first()
        user_data.skill_points -= points
        db.session.add(user_data)
        db.session.commit()


@views.route('/add-trick/<trick_name>/<trick_variant>', methods=['GET', 'POST'])
@login_required
def add_trick(trick_name, trick_variant):
    trick = Trick.query.filter(Trick.name == trick_name).first()
    variant = TrickVariant.query.filter(TrickVariant.name == trick_variant).first()
    trick_check = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                           UsersTricks.trick_variant_id == variant.id,
                                           UsersTricks.user_id == current_user.id).all()
    variant_count = len(UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                                 UsersTricks.user_id == current_user.id).all())
    default_date = date.today().isoformat()
    if not trick_check:
        if request.method == 'POST':
            note = request.form.get("note")
            set_date = request.form.get("date")
            new_date = datetime.fromisoformat(set_date)
            add_points(variant_count, trick.value)
            # if not file_name: FOR IMAGE OR VIDEO
            #     flash('Please fill in all the fields.', category='error')
            new_trick = UsersTricks(trick_id=trick.id, trick_variant_id=variant.id, user_id=current_user.id,
                                    content=note, created_at=new_date)
            db.session.add(new_trick)
            db.session.commit()
            flash('New trick added. Congratulations!', category='success')
            return redirect(url_for('views.my_trick', trick_name=trick_name))
    else:
        flash('You already added this trick', category='error')
        return redirect(url_for('views.my_trick', trick_name=trick_name))

    return render_template('tricks/create_users_tricks.html', trick=trick, variant=variant, date=default_date,
                           user=current_user)


@views.route('/trick-archive/<trick_name>/<trick_variant>')
@login_required
def trick_archive(trick_name, trick_variant):
    trick = Trick.query.filter(Trick.name == trick_name).first()
    variant = TrickVariant.query.filter(TrickVariant.name == trick_variant).first()
    trick_check = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                           UsersTricks.trick_variant_id == variant.id,
                                           UsersTricks.user_id == current_user.id).first()
    # TODO: jeśli nie ma rekordu to przekierowanie i flash
    return render_template('tricks/trick_archive.html', trick=trick, variant=variant, info=trick_check,
                           user=current_user)


@views.route('/edit-trick/<trick_name>/<trick_variant>', methods=['GET', 'POST'])
@login_required
def user_edit_trick(trick_name, trick_variant):
    trick = Trick.query.filter(Trick.name == trick_name).first()
    variant = TrickVariant.query.filter(TrickVariant.name == trick_variant).first()
    trick_check = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                           UsersTricks.trick_variant_id == variant.id,
                                           UsersTricks.user_id == current_user.id).first()
    if trick_check:
        if request.method == 'POST':
            note = request.form.get("note")
            date = request.form.get("date")
            trick_check.content = note
            if date:
                new_date = datetime.fromisoformat(date)
                trick_check.created_at = new_date
            db.session.add(trick_check)
            db.session.commit()
            flash('Trick edited.', category='success')
            return redirect(url_for('views.my_trick', trick_name=trick_name))
    else:
        flash("You haven't added this trick yet. ", category='error')
        return redirect(url_for('views.my_trick', trick_name=trick_name))
    return render_template('tricks/edit_trick.html', trick=trick, variant=variant, info=trick_check,
                           user=current_user)


@views.route('/delete-trick/<trick_name>/<trick_variant>', methods=['GET', 'POST'])
@login_required
def delete_trick(trick_name, trick_variant):
    trick = Trick.query.filter(Trick.name == trick_name).first()
    variant = TrickVariant.query.filter(TrickVariant.name == trick_variant).first()
    trick_to_delete = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                               UsersTricks.trick_variant_id == variant.id,
                                               UsersTricks.user_id == current_user.id).first()
    variant_count = len(UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                                 UsersTricks.user_id == current_user.id).all())
    subtract_points(variant_count, trick.value)
    db.session.delete(trick_to_delete)
    db.session.commit()
    return redirect(url_for('views.my_trick', trick_name=trick_name))


@views.route('/admin-console')
@login_required
@roles_required('admin')
def admin_console():
    return render_template("admin/admin_console.html", user=current_user)


@views.route('<category>/<slug>')
def show_post(slug, category):
    post_category = Category.query.filter(Category.name == category).first()
    post = Post.query.filter(Post.slug == slug).first()
    posts = Post.query.filter(Post.category_id == post_category.id).all()
    if post.image:
        return render_template('posts/post.html', post=post, posts=posts, user=current_user, category=post_category.name)
    else:
        return render_template('posts/post_no_image.html', post=post, posts=posts, user=current_user, category=post_category.name)


# TODO: DOKOŃCZYĆ WYŚWIETLANIE WSZYSTKICH POSTÓW - lista do edycji i usuwania
@views.route('/all-posts')
@login_required
@roles_required('admin')
def show_all_posts():
    posts = Post.query.all()
    return render_template('posts/show_posts.html', posts=posts, user=current_user)


@views.route('/create-post', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_post():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        file = request.files['file']
        category = request.form.get("category")

        # TODO: Default image if video not provided
        if not title or not content or not category:    # or not file
            flash('Please fill in all the fields.', category='error')
        elif file:
            filename = secure_filename(file.filename)
            # TODO: CONTENT TYPE filetype = file.content_type
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_post = Post(title=title, content=content, image=filename, category_id=category)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!', category='success')
        else:
            new_post = Post(title=title, content=content, image='', category_id=category)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!', category='success')
            # return redirect(url_for('views.admin_console'))

    return render_template("posts/create_post.html", user=current_user, categories=categories)


@views.route('/edit-post/<slug>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_post(slug):

    post_to_edit = Post.query.filter(Post.slug == slug).first()
    current_category = Category.query.filter(Category.id == post_to_edit.category_id).first()
    categories = Category.query.filter(Category.id != post_to_edit.category_id).all()

    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        file = request.files['file']
        category = request.form.get('category')
        if post_to_edit:
            filename = secure_filename(file.filename)

            if filename and filename != post_to_edit.image:
                # TODO: CONTENT TYPE filetype = file.content_type
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                post_to_edit.image = filename
            if title != post_to_edit.title:
                post_to_edit.slug = slugify(title)

            post_to_edit.title = title
            post_to_edit.content = content
            post_to_edit.category_id = category
            post_to_edit.edited_at = datetime.now()

            db.session.add(post_to_edit)
            db.session.commit()
            flash('Post edited!', category='success')
            return redirect(url_for('views.show_all_posts'))
        else:
            flash('Post not found.', category='error')
            return redirect(url_for('views.all-posts'))

    return render_template('posts/edit_post.html', post=post_to_edit,
                           user=current_user, current_category=current_category.name, categories=categories)


@views.route('/delete-post/<slug>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def delete_post(slug):
    post_to_delete = Post.query.filter(Post.slug == slug).first()
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('views.show_all_posts'))


@views.route('/create-trick', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_trick():
    if request.method == 'POST':
        name = request.form.get("name")
        if not name:
            flash('Please fill in all the fields.', category='error')
        else:
            new_trick = Trick(name=name)
            db.session.add(new_trick)
            db.session.commit()
            flash('Trick created!', category='success')
            # return redirect(url_for('views.admin_console'))

    return render_template("admin/create_trick.html", user=current_user)


@views.route('/create-variant', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_variant():
    if request.method == 'POST':
        name = request.form.get("name")
        if not name:
            flash('Please fill in all the fields.', category='error')
        else:
            new_variant = TrickVariant(name=name)
            db.session.add(new_variant)
            db.session.commit()
            flash('Variant created!', category='success')
            # return redirect(url_for('views.admin_console'))

    return render_template("admin/create_variant.html", user=current_user)


# TODO: post dratf?
