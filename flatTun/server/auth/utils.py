import jwt 
from functools import wraps

from server import *
from server.config import JWT_SECRET_KEY
from server.models.users import User as UserModel
from server.models.tokens import TokensBlacklist as TokensBlacklistModel

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = token = request.headers['x-access-token']
		if not token:
			response = make_response(jsonify(message='MissingToken'), 403)
			return response
		if TokensBlacklistModel.query.filter_by(expired_token=token).first():
			response = make_response(jsonify(message='ExpiredToken'), 403)
			return response
		try:
			data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
			current_user = UserModel.query.filter_by(id=data['id']).first()
		except:
			response = make_response(jsonify(message='InvalidToken'), 403)
			return response
		return f(current_user, *args, **kwargs)
	return decorator
