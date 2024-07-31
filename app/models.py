from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask_login import UserMixin
import secrets


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


friendship = sa.Table(
    'friendship', db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('friend_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    exercises: so.WriteOnlyMapped[List['Exercise']] = so.relationship('Exercise', back_populates='author', lazy='dynamic')
    weight_unit: so.Mapped[str] = so.mapped_column(sa.String(3), default='lbs')
    date_display: so.Mapped[str] = so.mapped_column(sa.String(10), default='%m/%d/%Y')
    friend_code: so.Mapped[str] = so.mapped_column(sa.String(6), index=True, unique=True, default=lambda: User.generate_friend_code())
    friends: so.WriteOnlyMapped[List['User']] = so.relationship(
        'User', secondary='friendship',
        primaryjoin=id == friendship.c.user_id,
        secondaryjoin=id == friendship.c.friend_id,
        backref='friend_of'
    )
    is_public: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    def __repr__(self):
        return f'<User: {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    @staticmethod
    def generate_friend_code():
        while True:
            code = secrets.token_hex(3).upper()[:6]
            if not db.session.scalar(sa.select(User).where(User.friend_code == code)):
                return code


class FriendRequest(db.Model):
    __tablename__ = 'friend_request'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    receiver_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    status: so.Mapped[str] = so.mapped_column(sa.String(20), default='pending')

    sender: so.Mapped[List['User']] = so.relationship('User', foreign_keys=[sender_id], backref='send_requests')
    receiver: so.Mapped[List['User']] = so.relationship('User', foreign_keys=[receiver_id], backref='received_requests')

    def __repr__(self):
        return f'<FriendRequest from {self.sender.username} to {self.receiver.username}, status: {self.status}>'


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    exercise_name: so.Mapped[str] = so.mapped_column(sa.String(100))

    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(User.id), index=True)
    author: so.Mapped[User] = so.relationship('User', back_populates='exercises')

    progressions: so.Mapped[List['Progression']] = so.relationship('Progression', back_populates='exercise', lazy=True, order_by='Progression.id', cascade='all, delete-orphan')

    def progression(self):
        progression_list = []
        for progression in self.progressions:
            progression_list.append(f'{progression.weight}{self.author.weight_unit} x {progression.rep} reps ({progression.simplified_date()})')
        return ' -> '.join(progression_list)

    def get_max(self):
        return max(self.progressions, key=lambda x: x.weight * x.rep).id

    def __repr__(self):
        return f'<Exercise: {self.exercise_name}, User: {self.author.username}>'


class Progression(db.Model):
    __tablename__ = 'progressions'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    rep: so.Mapped[int] = so.mapped_column(sa.Integer)
    weight: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), default=datetime.now(timezone.utc))
    exercise_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(Exercise.id), index=True)
    exercise: so.Mapped[Exercise] = so.relationship('Exercise', back_populates='progressions')

    def simplified_date(self):
        return self.date.strftime(self.exercise.author.date_display)

    def is_max(self):
        return self.id == self.exercise.get_max()
