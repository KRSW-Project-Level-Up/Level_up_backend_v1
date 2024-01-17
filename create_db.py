from app import app, db
from app.models import User, Game, Playlist, Wishlist, Rating

from sqlalchemy import inspect



with app.app_context():
    # Create the database and tables
    db.create_all()

    # Use the inspect method to check for table existence
    inspector = inspect(db.engine)
    if inspector.has_table('user'):  # Table names are typically lowercase
        print("User table exists.")
    else:
        print("User table does not exist.")

