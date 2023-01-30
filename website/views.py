from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint("views", __name__)


@views.route("/home")
@views.route("/")
def home():
    return render_template("home.html", user=current_user)


@views.route('/profile')
def profile():
    return "<h1>PROFILE</h1>"
