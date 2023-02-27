import random
import re

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User, UserData, Role

auth = Blueprint("auth", __name__)


# Validating email using simple regex expression
def is_email_valid(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
        return True
    else:
        return False


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not is_email_valid(email) or not user:
            flash('The email address or password is incorrect.')
        else:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)

                # admin is redirected to the admin panel, regular user to the home page
                if Role.query.filter_by(id=2).first() in current_user.roles:
                    print(type(current_user.roles))
                    return redirect(url_for('views.admin_console'))
                else:
                    return redirect(url_for('views.home'))

            else:
                flash('The email address or password is incorrect.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_exists = User.query.first()
        default_role = "user"

        # simple sign up form validation
        email_exists = User.query.filter_by(email=email).first()
        username_exists = UserData.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use', category='error')
        elif username_exists:
            flash('Please try another username', category='error')
        elif password2 != password1:
            flash("Provided passwords aren't matching. Please try again", category='error')
        elif len(username) < 2:
            flash('Your username is too short.', category='error')
        elif len(password1) < 8:
            flash('Your password is too short.', category='error')
        elif not is_email_valid(email):
            flash('Email incorrect', category='error')
        else:
            new_user = User(email=email, active=1,
                            password=generate_password_hash(password1, method='sha256',
                                                            salt_length=random.randint(17, 32)))
            new_user_data = UserData(username=username, user=new_user)

            # first user will be granted with an admin role
            if not user_exists:
                new_user.roles.append(Role.query.filter_by(id=2).first())
            else:
                new_user.roles.append(Role.query.filter_by(id=1).first())

            # Commit the changes to database
            db.session.add(new_user)
            db.session.add(new_user_data)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('New account created!')
            return redirect(url_for('views.home'))

    # POSSIBLE IMPROVEMENT: confirmation by email.

    return render_template("signup.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

# POSSIBLE IMPROVEMENT: change password
