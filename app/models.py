from flask_sqlalchemy import SQLAlchemy
from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(50))
    password = db.Column(db.String(80), nullable=False)
    userName = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.userName}>'
# Game model
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    # Additional fields like release_date, developer, etc. can be added here

    def __repr__(self):
        return f'<Game {self.title}>'
# Playlist model
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)  # Changed from String to DateTime

    user = db.relationship('User', backref=db.backref('playlists', lazy=True))
    game = db.relationship('Game', backref=db.backref('playlists', lazy=True))

    def __repr__(self):
        return f'<Playlist {self.user_id} {self.game_id}>'
# Wishlist model
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False) 

    user = db.relationship('User', backref=db.backref('wishlists', lazy=True))
    game = db.relationship('Game', backref=db.backref('wishlists', lazy=True))

    def __repr__(self):
        return f'<Wishlist {self.user_id} {self.game_id}>'
# Rating model
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    dislike_count = db.Column(db.Integer, default=0)

    game = db.relationship('Game', backref=db.backref('ratings', lazy=True))

    def __repr__(self):
        return f'<Rating for Game {self.game_id} - Likes: {self.like_count}, Dislikes: {self.dislike_count}>'
class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    action = db.Column(db.String(10))  # 'like' or 'dislike'

    def __repr__(self):
        return f'<UserRating {self.user_id} {self.game_id} {self.action}>'
