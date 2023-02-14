from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_manager, login_user
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = 'static/uploads'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = ",¦!©Îç4Kï'@0#yð¼9+,²ñF"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
