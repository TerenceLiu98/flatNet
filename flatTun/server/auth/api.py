from server import *
from server.config import JWT_SECRET_KEY
from server.models.users import User as UserModel
from server.models.tokens import TokensBlacklist as TokensBlacklistModel

from server.auth.utils import token_required


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
		return make_response(jsonify(user=user.username, id=user.id), 200)

class SignIn(Resource):
	def post(self):
		data = request.get_json()
		email, password = data.get("email"), data.get("password")
		if email is None or password is None:
			return make_response(jsonify(message='Missing arguments'), 400)
		user = UserModel.query.filter_by(email=email).first()
		if not user or not user.verify_password(password):
			return make_response(jsonify(message='Invalid username or password'), 400)
		token = user.generate_auth_token()
		response = make_response(jsonify(mesage="success"), 200)
		response.headers['x-access-token'] = token
		return response

class SignOut(Resource):
	@staticmethod
	@token_required
	def post(current_user):
		token = request.headers['x-access-token']
		token_status = TokensBlacklistModel.query.filter_by(expired_token=token).first()
		if token_status is not None:
			return jsonify(message='Token invalid', expired_token=f'{token}')
		token_status = TokensBlacklistModel(expired_token=token)
		database.session.add(token_status)
		database.session.commit()
		response = make_response(jsonify(message='success'), 200)
		return response
		
class TokenRefresh(Resource):
	@staticmethod
	@token_required
	def get(current_user):
		token = request.headers['x-access-token']
		token_status = TokensBlacklistModel.query.filter_by(expired_token=token).first()
		if token_status is None:
			expired_token = TokensBlacklistModel(expired_token=token)
			database.session.add(expired_token)
			database.session.commit()
			token = current_user.generate_auth_token()
			response = make_response(jsonify(message="success"), 200)
			response.headers['x-access-token'] = token
		return response