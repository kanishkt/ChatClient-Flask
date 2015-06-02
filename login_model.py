from flask.ext.login import UserMixin
from flask.ext.user import UserMixin
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from setup import app, test_config
__author__ = 'kanishk'

'''
Models for Flask-Login
'''

 # Load local_settings.py if file exists
try: app.config.from_object('local_settings')
except: pass

# Load optional test_config
if test_config:
    app.config.update(test_config)

# Initialize Flask extensions
mail = Mail(app)                                # Initialize Flask-Mail
db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy


'''
Class to Define a User Data Model
'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    # Relationships
    user_auth = db.relationship('UserAuth', uselist=False)
    roles = db.relationship('Role', secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'))
'''
Class to Define the UserAuth data model
'''
class UserAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

    # Relationships
    user = db.relationship('User', uselist=False)
'''
Class to Define the Role data model
'''
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

'''
Class to Define the UserRoles data model
'''
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))