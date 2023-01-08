from modules import *
from modules.config import JWT_SECRET_KEY
from modules.models.users import User as UserModel
from modules.models.tokens import TokensBlacklist as TokensBlacklistModel
import jwt 
import logging
from functools import wraps

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = token = request.headers['x-access-tokens']
		if not token:
			return jsonify({'message': 'a valid token is missing'})
		if TokensBlacklistModel.query.filter_by(expired_token=token).first():
			return jsonify({'message': 'token is expired'})
		try:
			data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
			current_user = UserModel.query.filter_by(id=data['id']).first()
		except:
			return jsonify({'message': 'token is invalid'})
		return f(current_user, *args, **kwargs)
	return decorator
		

class SignUp(Resource):
	@staticmethod
	def post():
		username, password, email = request.json.get("username"), request.json.get("password"), request.json.get("email")
		if username is None or password is None or email is None:
			return jsonify(message='Missing arguments')
		if UserModel.query.filter_by(username=username).first() is not None:
			return jsonify(message='User already exists')
		if UserModel.query.filter_by(email=email).first() is not None:
			return jsonify(message='User already exists')
		user = UserModel(username=username, email=email)
		user.generate_id()
		user.generate_password(password)
		database.session.add(user)
		database.session.commit()
		return jsonify(user=user.username, id=user.id)

class SignIn(Resource):
	def post(self):
		data = request.get_json()
		email, password = data.get("email"), data.get("password")
		#email, password = request.json.get("email"), request.json.get("password")
		if email is None or password is None:
			return jsonify(message='Missing arguments')
		user = UserModel.query.filter_by(email=email).first()
		if not user or not user.verify_password(password):
			return jsonify(message='Invalid username or password')
		token = user.generate_auth_token()
		return jsonify({'token': token, 'duration': 600})

class SignOut(Resource):
	@staticmethod
	@token_required
	def post(current_user):
		token = request.headers['x-access-tokens']
		token_status = TokensBlacklistModel.query.filter_by(expired_token=token).first()
		if token_status is not None:
			return jsonify(message='Token invalid', expired_token=f'{token}')
		token_status = TokensBlacklistModel(expired_token=token)
		database.session.add(token_status)
		database.session.commit()
		g.user = None
		return jsonify(message='Token expired', expired_token=f'{token}')
		
	
		
class UserToken(Resource):
	@staticmethod
	@token_required
	def get(current_user):
		token = current_user.generate_auth_token()
		return jsonify({'token': token, 'duration': 600})
	
class Resources(Resource):
	@staticmethod
	@token_required
	def get(current_user):
		return jsonify(data="{}".format(current_user.username))