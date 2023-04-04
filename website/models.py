from . import db
import re
from time import time

from unidecode import unidecode

from flask_security import UserMixin, RoleMixin

from sqlalchemy.sql import func

# Create table in database for user_role relationship
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


# Function that processes title of a post and returns a slug.
def slugify(post_title):
    pattern = r'[^\w+]'
    title = unidecode(post_title)
    return str.lower(re.sub(pattern, '-', title))
    # TODO: Slugify does not work properly


# Create table in database for storing users
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    active = db.Column(db.Boolean())
    user_data = db.relationship("UserData", uselist=False, backref="user")
    # backreferences the user_id from roles_users table
    roles = db.relationship('Role', secondary=roles_users)
    users_ticks = db.relationship('UsersTricks', backref='user')


# Create table in database for storing additional user data
class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    skill_points = db.Column(db.Float)


# Create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    post = db.relationship("Post", uselist=False, backref="post")


# Create table in database for storing posts
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(140))
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    edited_at = db.Column(db.DateTime(timezone=True), default=func.now())
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        else:
            self.slug = str(int(time()))


# TODO: set correct nullability


# TODO: slug for trick and variant
# Create table in database for storing tricks
class Trick(db.Model):
    __tablename__ = 'trick'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    users_ticks = db.relationship('UsersTricks', backref='trick')
    value = db.Column(db.Integer)


# Create table in database for storing tricks
class TrickVariant(db.Model):
    __tablename__ = 'trick_variant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    users_ticks = db.relationship('UsersTricks', backref='trick_variant')


class UsersTricks(db.Model):
    __tablename__ = 'users_ticks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trick_id = db.Column(db.Integer, db.ForeignKey('trick.id'))
    trick_variant_id = db.Column(db.Integer, db.ForeignKey('trick_variant.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    content = db.Column(db.Text)
    # TODO: można dodać fotkę lub film

