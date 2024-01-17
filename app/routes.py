from flask import request, jsonify
from werkzeug.security import generate_password_hash
from . import app, db
from werkzeug.security import check_password_hash
from datetime import datetime
from .models import User, Game, Playlist, Wishlist, Rating, UserRating
from .utils import hash_password
from app.models import User, Game, Playlist, Wishlist, Rating, UserRating
import jwt
from flask import current_app
from flask_cors import cross_origin
from datetime import datetime




@app.route('/')
def home():
    return "Welcome to the Flask App!"

@app.route('/signup', methods=['POST'])
def signup():
    # Extracting data from request
    data = request.json
    email = data.get('email')
    username = data.get('userName')
    password = data.get('password')

    # Check if user already exists
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'message': 'Email already in use'}), 409

    if User.query.filter_by(userName=username).first() is not None:
        return jsonify({'message': 'Username already in use'}), 409

    # Hashing the password
    hashed_password = generate_password_hash(password)

    # Creating new user object
    new_user = User(
        email=email,
        userName=username,
        password=hashed_password,
        firstName=data.get('firstName'),
        lastName=data.get('lastName'),
        age=data.get('age'),
        nationality=data.get('nationality')
    )

    # Adding new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/signin', methods=['POST'])
@cross_origin() # Allow CORS for this API endpoint
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # Generate the token
        token_data = {
            'user_id': user.id,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email,
            'userName': user.userName,
            'age': user.age,
            'nationality':user.nationality,
        }
        token = jwt.encode(token_data, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token, 'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    


@app.route('/addtoplaylist', methods=['POST'])
@cross_origin() 
def add_to_playlist():
    data = request.json
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    date_added_str = data.get('date_added')

    # Check if user_id or game_id is None
    if not user_id or not game_id:
        return jsonify({'message': 'Missing user_id or game_id'}), 400

    # Parse the date
    try:
        date_added = datetime.strptime(date_added_str, '%Y-%m-%d') if date_added_str else datetime.utcnow()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    # Verify user and game exist
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Check if the game is already in the playlist
    existing_entry = Playlist.query.filter_by(user_id=user_id, game_id=game_id).first()
    if existing_entry:
        return jsonify({'message': 'Game already in playlist'}), 409

    # Create new Playlist entry
    new_entry = Playlist(user_id=user_id, game_id=game_id, date_added=date_added)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'Game added to playlist'}), 201


@app.route('/addtowishlist', methods=['POST'])
@cross_origin()  
def add_to_wishlist():
    data = request.json
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    date_added_str = data.get('date_added')

    # Check if user_id or game_id is None
    if not user_id :
        return jsonify({'message': 'Missing user_id or game_id'}), 400
      # Check if the game is already in the playlist
    existing_entry = Wishlist.query.filter_by(user_id=user_id, game_id=game_id).first()
    if existing_entry:
        return jsonify({'message': 'Game already in Wishlist'}), 409
    # Parse the date
    try:
        date_added = datetime.strptime(date_added_str, '%Y-%m-%d') if date_added_str else datetime.utcnow()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    # Verify user and game exist
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Create new Wishlist entry
    new_wishlist_item = Wishlist(user_id=user_id, game_id=game_id, date_added=date_added)
    db.session.add(new_wishlist_item)
    db.session.commit()

    return jsonify({'message': 'Game added to wishlist'}), 201

@app.route('/getallplaylist/<int:user_id>', methods=['GET'])
@cross_origin()
def get_all_playlist(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Query all playlist entries for the user
    playlist_items = Playlist.query.filter_by(user_id=user_id).all()

    playlist_data = []
    for item in playlist_items:
        # Count likes and dislikes for each game
        like_count = UserRating.query.filter_by(game_id=item.game_id, action='like').count()
        dislike_count = UserRating.query.filter_by(game_id=item.game_id, action='dislike').count()

        playlist_data.append({
            'game_id': item.game_id,
            'date_added': item.date_added,
            'like_count': like_count,
            'dislike_count': dislike_count
        })

    return jsonify({'playlist': playlist_data}), 200


@app.route('/getallwishlist/<int:user_id>', methods=['GET'])
@cross_origin()  
def get_all_wishlist(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

   
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    wishlist_data =  [{'game_id': item.game_id, 'date_added': item.date_added} for item in wishlist_items]

    return jsonify({'wishlist': wishlist_data}), 200


@app.route('/updategamerating', methods=['POST'])
@cross_origin() 
def update_game_rating():
    data = request.json
    game_id = data.get('game_id')
    user_id = data.get('user_id')
    action = data.get('action')  # 'like' or 'dislike'

    user_rating = UserRating.query.filter_by(user_id=user_id, game_id=game_id).first()

    if user_rating:
        if user_rating.action != action:
            user_rating.action = action
    else:
        new_user_rating = UserRating(user_id=user_id, game_id=game_id, action=action)
        db.session.add(new_user_rating)

    db.session.commit()

    # Calculate the total likes and dislikes
    total_likes = UserRating.query.filter_by(game_id=game_id, action='like').count()
    total_dislikes = UserRating.query.filter_by(game_id=game_id, action='dislike').count()

    return jsonify({
        'message': 'Rating updated successfully',
        'game_id': game_id,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes
    }), 200

def update_aggregate_rating(game_id):
    like_count = UserRating.query.filter_by(game_id=game_id, action='like').count()
    dislike_count = UserRating.query.filter_by(game_id=game_id, action='dislike').count()

    rating = Rating.query.filter_by(game_id=game_id).first()
    if not rating:
        rating = Rating(game_id=game_id, like_count=like_count, dislike_count=dislike_count)
        db.session.add(rating)
    else:
        rating.like_count = like_count
        rating.dislike_count = dislike_count

@app.route('/deletefromwishlist', methods=['POST'])
@cross_origin() 
def delete_from_wishlist():
    data = request.json
    user_id = data.get('user_id')
    game_id = data.get('game_id')

    wishlist_item = Wishlist.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not wishlist_item:
        return jsonify({'message': 'Item not found in wishlist'}), 404

    db.session.delete(wishlist_item)
    db.session.commit()

    return jsonify({'message': 'Item deleted from wishlist'}), 200

@app.route('/deletefromplaylist', methods=['POST'])
def delete_from_playlist():
    data = request.json
    user_id = data.get('user_id')
    game_id = data.get('game_id')

    playlist_item = Playlist.query.filter_by(user_id=user_id, game_id=game_id).first()
    if not playlist_item:
        return jsonify({'message': 'Item not found in playlist'}), 404

    db.session.delete(playlist_item)
    db.session.commit()

    return jsonify({'message': 'Item deleted from playlist'}), 200
@app.route('/updateuserinfo', methods=['PUT'])
@cross_origin() # Allow CORS for this API endpoint
def update_user_info():
    data = request.json
    user_id = data.get('user_id')

    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Update fields if they are in the request
    if 'email' in data:
        user.email = data['email']
    if 'firstName' in data:
        user.firstName = data['firstName']
    if 'lastName' in data:
        user.lastName = data['lastName']
    if 'age' in data:
        user.age = data['age']
    if 'nationality' in data:
        user.nationality = data['nationality']

    # Save the changes to the database
    db.session.commit()

    # Generate a new token with updated user info
    token_data = {
        'user_id': user.id,
        'firstName': user.firstName,
        'lastName': user.lastName,
        'email': user.email,
        'userName': user.userName,
        'age': user.age,
        'nationality': user.nationality,
    }
    new_token = jwt.encode(token_data, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': new_token, 'message': 'User info updated successfully'}), 200
