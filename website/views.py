from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for
from flask_login import login_required, current_user
from flask_security import roles_required
from werkzeug.utils import secure_filename
from datetime import datetime, date

import os

from . import db
from .models import Post, Trick, TrickVariant, User, Role, roles_users, UsersTricks, UserData, slugify, Category, DictionaryPhrase

views = Blueprint("views", __name__)


@views.context_processor
def inject_menu_items():
    trick_post = Post.query.filter(Post.category_id == 2).first()
    trick_category = Category.query.filter(Category.id == 2).first()

    about_post = Post.query.filter(Post.category_id == 3).first()
    about_category = Category.query.filter(Category.id == 3).first()
    return dict(menu_trick_post=trick_post, menu_trick_category=trick_category,
                menu_about_post=about_post, menu_about_category=about_category)


# @views.route("/")
# def intro():
#     return render_template("intro.html", user=current_user)


@views.errorhandler(404)
def not_found(e):
    return render_template('404.html', user=current_user)


@views.route('/')
def home():
    return render_template("home.html", user=current_user)


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

    # passing object to template in order to create link using url_for
    add_trick_link = Trick.query.first()

    return render_template('user/profile.html', user=current_user, tricks=u_tricks, user_data=user_data,
                           trick=add_trick_link)


@views.route('/trick/<trick_slug>')
@login_required
def my_trick(trick_slug):
    trick = Trick.query.filter(Trick.slug == trick_slug).first()
    tricks = Trick.query.all()

    # Trick variants that already been done by the current user - query result in tuples
    completed_variants = db.session.query(UsersTricks.trick_variant_id).filter_by(trick_id=trick.id,
                                                                                  user_id=current_user.id).all()
    # Tuple to int conversion
    user_variants = [int(t[0]) for t in completed_variants]

    trick_article = Post.query.filter(Post.slug == trick_slug).first()
    if trick_article:
        article = True
    else:
        article = False

    variants = TrickVariant.query.all()

    return render_template('my_tricks.html', trick=trick, tricks=tricks,
                           user=current_user, all_variants=variants, user_variants=user_variants, article=article)


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


@views.route('/add-trick/<trick_slug>/<variant_slug>', methods=['GET', 'POST'])
@login_required
def add_trick(trick_slug, variant_slug):
    trick = Trick.query.filter(Trick.slug == trick_slug).first()
    variant = TrickVariant.query.filter(TrickVariant.slug == variant_slug).first()
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
            flash('Gratulacje! Dodałeś nowy trick.', category='success')
            return redirect(url_for('views.my_trick', trick_slug=trick_slug))
    else:
        flash('Dodałeś już taki trick', category='error')
        return redirect(url_for('views.my_trick', trick_slug=trick_slug))

    return render_template('tricks/create_users_tricks.html', trick=trick, variant=variant, date=default_date,
                           user=current_user)


# @views.route('/trick-archive/<trick_slug>/<variant_slug>')
# @login_required
# def trick_archive(trick_slug, variant_slug):
#     trick = Trick.query.filter(Trick.slug == trick_slug).first()
#     variant = TrickVariant.query.filter(TrickVariant.slug == variant_slug).first()
#     trick_check = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
#                                            UsersTricks.trick_variant_id == variant.id,
#                                            UsersTricks.user_id == current_user.id).first_or_404()
#     return render_template('tricks/trick_archive.html', trick=trick, variant=variant, info=trick_check,
#                            user=current_user)


@views.route('/edit-trick/<trick_slug>/<variant_slug>', methods=['GET', 'POST'])
@login_required
def user_edit_trick(trick_slug, variant_slug):
    trick = Trick.query.filter(Trick.slug == trick_slug).first()
    variant = TrickVariant.query.filter(TrickVariant.slug == variant_slug).first()
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
            flash('Zmiany zostały zapisane', category='success')
            return redirect(url_for('views.profile'))
    else:
        flash("Nie dodałeś jeszcze takiego tricku", category='error')
        return redirect(url_for('views.my_trick', trick_slug=trick_slug))
    return render_template('tricks/edit_trick.html', trick=trick, variant=variant, info=trick_check,
                           user=current_user)


@views.route('/delete-trick/<trick_slug>/<variant_slug>', methods=['GET', 'POST'])
@login_required
def delete_user_trick(trick_slug, variant_slug):
    trick = Trick.query.filter(Trick.slug == trick_slug).first()
    variant = TrickVariant.query.filter(TrickVariant.slug == variant_slug).first()
    trick_to_delete = UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                               UsersTricks.trick_variant_id == variant.id,
                                               UsersTricks.user_id == current_user.id).first()
    variant_count = len(UsersTricks.query.filter(UsersTricks.trick_id == trick.id,
                                                 UsersTricks.user_id == current_user.id).all())
    subtract_points(variant_count, trick.value)
    db.session.delete(trick_to_delete)
    db.session.commit()
    return redirect(url_for('views.profile'))


@views.route('/admin-console')
@login_required
@roles_required('admin')
def admin_console():
    return render_template("admin/admin_console.html", user=current_user)



@views.route('<category>/<slug>')
def show_post(slug, category):
    post_category = Category.query.filter(Category.name == category).first_or_404()
    post = Post.query.filter(Post.slug == slug).first_or_404()
    posts = Post.query.filter(Post.category_id == post_category.id).all()
    if post.media:
        return render_template('posts/post.html', post=post, posts=posts,
                               user=current_user, category=post_category.name)
    else:
        return render_template('posts/post_no_image.html', post=post, posts=posts,
                               user=current_user, category=post_category.name)



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

        title_validation = Post.queru.filter(Post.title == title).first()

        if not title or not content or not category:    # or not file
            flash('Please fill in all the fields.', category='error')
        elif title_validation:
            flash('Post o takim tytule już istnieje - zmień tytuł', category='error')
            render_template("posts/create_post.html", user=current_user, categories=categories)
        elif file:
            filename = secure_filename(file.filename)
            mimetype = file.content_type
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_post = Post(title=title, content=content, media=filename, category_id=category, mimetype=mimetype)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!', category='success')
        else:
            new_post = Post(title=title, content=content, media='', category_id=category, mimetype='')
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
        if 'delete_file' in request.form:
            post_to_edit.media = ''
            post_to_edit.mimetype = ''
            db.session.add(post_to_edit)
            db.session.commit()
            return redirect(url_for('views.edit_post', slug=slug))
        else:
            title = request.form.get("title")
            content = request.form.get("content")
            file = request.files['file']
            category = request.form.get('category')
            if post_to_edit:
                filename = secure_filename(file.filename)

                if filename and filename != post_to_edit.media:
                    mimetype = file.content_type
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    post_to_edit.mimetype = mimetype
                    post_to_edit.media = filename
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


@views.route('/dictionary')
def dictionary():
    phrases = DictionaryPhrase.query.order_by(DictionaryPhrase.title)
    return render_template('dictionary/dictionary.html', user=current_user, phrases=phrases)


@views.route('/add-phrase', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def add_phrase():
    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            flash('Please fill in all the fields.', category='error')
        else:
            new_phrase = DictionaryPhrase(title=title, content=content)
            db.session.add(new_phrase)
            db.session.commit()
            flash('Phrase created!', category='success')
            # return redirect(url_for('views.admin_console'))
    return render_template('dictionary/add_phrase.html', user=current_user)


@views.route('/edit-phrase/<slug>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_phrase(slug):

    phrase_to_edit = DictionaryPhrase.query.filter(DictionaryPhrase.slug == slug).first()

    if request.method == 'POST':
        title = request.form.get("title")
        content = request.form.get("content")
        if phrase_to_edit:
            if not title or not content:
                flash('Please fill in all the fields.', category='error')
            else:
                if title != phrase_to_edit.title:
                    phrase_to_edit.slug = slugify(title)
                    print(phrase_to_edit.slug)
                phrase_to_edit.title = title
                phrase_to_edit.content = content
                db.session.add(phrase_to_edit)
                db.session.commit()
                flash('Fraza została zaktualizowana!', category='success')
                return redirect(url_for('views.dictionary', _anchor=phrase_to_edit.slug))
        else:
            flash('Fraza nie została znaleziona.', category='error')
            return redirect(url_for('views.admin_console'))
    return render_template('dictionary/edit_phrase.html', user=current_user, phrase=phrase_to_edit)


@views.route('/show_tricks', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def show_tricks():
    tricks = Trick.query.all()
    return render_template("admin/show_tricks.html", tricks=tricks, user=current_user)


@views.route('/create-trick', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_trick():
    if request.method == 'POST':
        name = request.form.get("name")
        points = request.form.get("points")
        tutorial_link = request.form.get("tutorial_link")
        if not name and not points:
            flash('Please fill in all the fields.', category='error')
        else:
            new_trick = Trick(name=name, points=points, link=tutorial_link)
            db.session.add(new_trick)
            db.session.commit()
            flash('Trick created!', category='success')
            # return redirect(url_for('views.admin_console'))

    return render_template("admin/create_trick.html", user=current_user)


@views.route('/edit-trick/<slug>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_trick(slug):
    trick_to_edit = Trick.query.filter(Trick.slug == slug).first()

    if request.method == 'POST':
        name = request.form.get("name")
        points = request.form.get("points")
        tutorial_link = request.form.get("tutorial_link")
        if not trick_to_edit:
            flash('Trick nie istnieje', category='error')
            return redirect(url_for('views.admin_console'))
        else:
            if trick_to_edit.name != name:
                trick_to_edit.slug = slugify(name)
            trick_to_edit.name, trick_to_edit.points, trick_to_edit.tutorial_link = name, points, tutorial_link
            db.session.add(trick_to_edit)
            db.session.commit()
            flash('Trick created!', category='success')
            return redirect(url_for('views.show_tricks'))

    return render_template("admin/edit_trick.html", trick=trick_to_edit, user=current_user)


@views.route('/delete-trick/<slug>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def delete_trick(slug):
    trick_to_delete = Trick.query.filter(Trick.slug == slug).first()
    db.session.delete(trick_to_delete)
    db.session.commit()
    return redirect(url_for('views.show_tricks'))


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


@views.route('/users', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def show_users():
    users = db.session.query(User).filter(User.id != current_user.id).all()

    return render_template("admin/show_users.html", user=current_user, users=users)


@views.route('/deactivate/<u_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def deactivate_user(u_id):
    if request.method == 'POST' and 'deactivate' in request.form:
        d_user = User.query.filter(User.id == u_id).first()
        if d_user.active == 1:
            d_user.active = 0
        else:
            d_user.active = 1
        db.session.add(d_user)
        db.session.commit()
    return redirect(url_for('views.show_users'))


@views.route('/learn-more')
@login_required
def learn_more():
    return render_template("learn_more.html", user=current_user)
