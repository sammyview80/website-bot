from flask import Blueprint, request, jsonify, session
from models import db, UserModal
from flask_bcrypt import Bcrypt

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = data['password']

    userExists = UserModal.query.filter_by(email=email).first() is not None
    if userExists:
        return jsonify({'message': 'User already exists'}), 409
    hash_password = bcrypt.generate_password_hash(password)
    user = UserModal(email=email, password=hash_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'email': user.email
    }), 201

@auth.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    user = UserModal.query.filter_by(id=user_id).first()
    return jsonify({
        'id': user.id,
        'email': user.email
    }), 200

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    user = UserModal.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    session['user_id'] = user.id

    return jsonify({
        'id': user.id,
    }), 200
