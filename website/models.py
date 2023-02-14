from . import db
import re
from time import time

from flask_security import UserMixin, RoleMixin

from sqlalchemy.sql import func


# Create table in database for user_role relationship
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


# Function that processes title of a post and returns a slug.
def slugify(post_title):
    pattern = r'[^\w+]'
    return str.lower(re.sub(pattern, '-', post_title))
    # TODO: Slugify does not work properly
    #  (python-slugify package may help)


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


# Create table in database for storing additional user data
class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# Create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        else:
            self.slug = str(int(time()))

# TODO: set correct nullability
# TODO: implement user roles (normalize User table)
