import jwt 
import time
from functools import wraps

from server import *
from server.config import JWT_SECRET_KEY
from server.models.users import User as UserModel, Role
from server.models.tokens import TokensBlacklist as TokensBlacklistModel


#TODO: RBAC
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

def check_permission(role, permission):
	role_needed = Role.filter_by(id=role).first()
	return (role_needed.permissions & permission) == permission

def token_required_role(permission):
	def decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
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
			user_permission = Role.query.filter_by(id=data["role"]).first()
			if user_permission.name not in permission:
				response = make_response(jsonify(message='Permission Denied'), 403)
				return response
			return f(current_user, *args, **kwargs)
		return wrapper
	return decorator
			