from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_manager, login_user
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_migrate import Migrate

db = SQLAlchemy()
# ckeditor = CKEditor()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.DevelopmentConfig")
    # ckeditor.init_app(app)
    db.init_app(app)

    migrate = Migrate(app, db, render_as_batch=True)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from . import models

    with app.app_context():
        db.create_all()
        print("Created Database!")

    l_manager = LoginManager()
    l_manager.login_view = "auth.login"
    l_manager.init_app(app)

    @l_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    user_datastore = SQLAlchemySessionUserDatastore(db.session, models.User, models.Role)
    security = Security(app, user_datastore)

    return app
