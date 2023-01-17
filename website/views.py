from flask import Blueprint, render_template

views = Blueprint("views", __name__)


@views.route("/home")
@views.route("/")
def home():
    return render_template("home.html", name="Marek")


@views.route('/profile')
def profile():
    return "<h1>PROFILE</h1>"
