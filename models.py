#!/usr/bin/env python
import time
import random
from passlib.hash import pbkdf2_sha512 as sha512

from extensions import db

class AuthToken(db.Model):
    __tablename__ = 'auth_token'
    id = db.Column (db.Integer, primary_key=True)
    token_type = db.Column(db.String(40), default='bearer')
    access_token = db.Column(db.String(64), unique=True, nullable=False)
    refresh_token = db.Column(db.String(64), index=True)
    revoked = db.Column(db.Boolean, default=False)
    issued_at = db.Column(db.Integer, nullable=False, default=lambda: int(time.time()))
    expires_in = db.Column(db.Integer, nullable=False, default=86400)
    user_id = db.Column(db.Integer, db.ForeignKey('api_user.id', ondelete='CASCADE'))
    user = db.relationship('APIUser')

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + self.expires_in

    def get_is_expired(self):
        return self.get_expires_at <= int(time.time())

    @staticmethod
    def generate_token():
        return ''.join([str(y) for x in range(64) for y in random.choice('0123456789abcdef')])

    def generate_token_set(self):
        self.access_token = self.generate_token()
        self.refresh_token = self.generate_token()
        self.revoked = False
        self.issued_at = int(time.time())
        return True

    def generate_token_access(self):
        self.access_token = generate_token()
        self.issued_at = int(time.time())
        return True

class APIUser(db.Model):
    __tablename__ = 'api_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def hash_password(self, password):
        self.password_hash = sha512.hash(password)

    def verify_password(self, password):
        return sha512.verify(password, self.password_hash)