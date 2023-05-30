from . import db
import re
from time import time

from unidecode import unidecode

from flask_security import UserMixin, RoleMixin

from sqlalchemy.sql import func

from sqlalchemy import event


# Create table in database for user_role relationship
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


# Function that processes title of a post and returns a slug.
def slugify(post_title):
    pattern = r'[^\w+]'
    title = unidecode(post_title)
    return str.lower(re.sub(pattern, '-', title))


# Create table in database for storing users
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    active = db.Column(db.Boolean())
    user_data = db.relationship("UserData", uselist=False, backref="user")
    # backreferences the user_id from roles_users table
    roles = db.relationship('Role', secondary=roles_users, backref="user")
    users_ticks = db.relationship('UsersTricks', backref='user')


# Create table in database for storing additional user data
class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    skill_points = db.Column(db.Float, default=0)


# Create table in database for storing roles
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)


@event.listens_for(Role.__table__, 'after_create')
def create_roles(*args, **kwargs):
    db.session.add(Role(name='user'))
    db.session.add(Role(name='admin'))
    db.session.commit()


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    post = db.relationship("Post", uselist=False, backref="post")


@event.listens_for(Category.__table__, 'after_create')
def create_categories(*args, **kwargs):
    db.session.add(Category(name='default'))
    db.session.add(Category(name='tricki'))
    db.session.add(Category(name='inne'))
    db.session.commit()


class DictionaryPhrase(db.Model):
    __tablename__ = 'dictionary_phrase'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    content = db.Column(db.Text)
    # source = db.Column(db.String(200))
    # is_source_a_link = db.Column(db.Boolean())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        else:
            self.slug = str(int(time()))


# Create table in database for storing posts
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    media = db.Column(db.String(140), default='')
    mimetype = db.Column(db.String(50))
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


@event.listens_for(Post.__table__, 'after_create')
def create_posts(*args, **kwargs):
    db.session.add(Post(title='Hello trick', content='Default post for category: triki', category_id=2))
    db.session.add(Post(title='Hello inne', content='Default post for category: inne', category_id=3))
    db.session.commit()


# Create table in database for storing tricks
class Trick(db.Model):
    __tablename__ = 'trick'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    slug = db.Column(db.String(140))
    users_ticks = db.relationship('UsersTricks', backref='trick')
    value = db.Column(db.Integer)
    tutorial_link = db.Column(db.String(140))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)
        else:
            self.slug = str(int(time()))


@event.listens_for(Trick.__table__, 'after_create')
def create_tricks(*args, **kwargs):
    db.session.add(Trick(name='Ollie', value=10))
    db.session.add(Trick(name='Nollie', value=10))
    db.session.add(Trick(name='Kickflip', value=20))
    db.session.add(Trick(name='Heel flip', value=20))
    db.session.add(Trick(name='360 flip', value=40))
    db.session.add(Trick(name='Impossible', value=50))
    db.session.commit()


# Create table in database for storing tricks
class TrickVariant(db.Model):
    __tablename__ = 'trick_variant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    slug = db.Column(db.String(140))
    users_ticks = db.relationship('UsersTricks', backref='trick_variant')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)
        else:
            self.slug = str(int(time()))


@event.listens_for(TrickVariant.__table__, 'after_create')
def create_tricks(*args, **kwargs):
    db.session.add(TrickVariant(name='normal'))
    db.session.add(TrickVariant(name='switch'))
    db.session.add(TrickVariant(name='nollie'))
    db.session.add(TrickVariant(name='fakie'))
    db.session.commit()


class UsersTricks(db.Model):
    __tablename__ = 'users_ticks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trick_id = db.Column(db.Integer, db.ForeignKey('trick.id'))
    trick_variant_id = db.Column(db.Integer, db.ForeignKey('trick_variant.id'))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    content = db.Column(db.Text)

