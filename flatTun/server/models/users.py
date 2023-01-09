from server import *
from server.config import JWT_SECRET_KEY
from server.utils import uuid_generator

from dataclasses import dataclass

import jwt
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Permissions:
	USER_MANAGE = 0x01
	USERINFO = 0x02
	NETSPACES_MANAGE = 0x03
	NODE_GET = 0x04
	NODE_PUT = 0x05
	NODES_GET = 0x06
	NODES_PUT = 0x07


@dataclass
class Role(database.Model):
	__tablename__ = "role"
	id: int = database.Column("id", database.Integer, primary_key=True)
	name: str = database.Column("name", database.String(16), nullable=False)
	permissions: int = database.Column("permissions", database.Integer, nullable=False)
	@staticmethod
	def init():
		admin = Role(name="admin", permissions = Permissions.USER_MANAGE)
		user = Role(name="user", permissions = Permissions.USERINFO + Permissions.NETSPACES_MANAGE + Permissions.NODE_GET + Permissions.NODE_PUT + Permissions.NODES_GET + Permissions.NODES_PUT)	
		supernode = Role(name="supernode", permissions = Permissions.NODE_GET + Permissions.NODE_PUT + Permissions.NODES_GET + Permissions.NODES_PUT)
		node = Role(name="node", permissions = Permissions.NODE_GET + Permissions.NODE_PUT)
		database.session.add(admin)
		database.session.add(user)
		database.session.add(supernode)
		database.session.add(node)
	def reset_perssions(self):
		self.permissions = 0
	
	def has_permission(self, permission):
		return self.permissions & permission == permission
	
	def add_permission(self, permission):
		if not self.has_permission(permission):
			self.permissions += permission

@dataclass
class User(database.Model):
	__tablename__ = "users"
	id:str = database.Column("id", database.String(36), nullable=False)
	username:str = database.Column("username", database.String(16), nullable=False)
	password:str = database.Column("password", database.String(128), nullable=False)
	email:str = database.Column("email", database.String(16), primary_key=True, nullable=False) # email as the primary key
	created: datetime = database.Column("created", database.DateTime, default=database.func.now())
	role: int = database.Column("role", database.Integer, nullable=False)

	def generate_id(self):
		self.id = uuid_generator(form="user")
		
	def generate_password(self, password):
		self.password = generate_password_hash(password)
        
	def verify_password(self, password):
		return check_password_hash(self.password, password) 
	
	def assign_role(self):
		if Role.query.filter_by(name="user").first() is None:
			Role.init()
		self.role = Role.query.filter_by(name="user").first().id
	
	def generate_auth_token(self, headers=None, expiration=7200):
			try:
				role = headers["x-client"]
			except:
				role = self.role
			return jwt.encode({'id': self.id, "role": role,
								 "exp": time.time() + expiration}, JWT_SECRET_KEY, algorithm='HS256')

	@staticmethod
	def verify_auth_token(token):
		try:
			data = jwt.decode(token, JWT_SECRET_KEY,algorithms=['HS256'])
		except Exception as e:
			return None
		return User.query.get(data['id'])