"""
User account model stored in MongoDB via mongoengine.

We intentionally do NOT use Django's built-in auth.User model because all
application data must live in MongoDB. Passwords are still hashed using
Django's own PBKDF2 hasher (django.contrib.auth.hashers), so password
storage is just as secure as a normal Django project.
"""
import datetime
import uuid

from django.contrib.auth.hashers import check_password, make_password
from mongoengine import BooleanField, DateTimeField, Document, EmailField, StringField


class User(Document):
    user_id = StringField(default=lambda: uuid.uuid4().hex, unique=True)
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    full_name = StringField(required=True, max_length=120)
    phone = StringField(max_length=20, default='')
    password_hash = StringField(required=True)
    is_admin = BooleanField(default=False)
    is_active = BooleanField(default=True)
    date_joined = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': ['username', 'email', 'user_id'],
        'ordering': ['-date_joined'],
    }

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.username
