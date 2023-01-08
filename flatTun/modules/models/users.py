from modules import *
from modules.config import JWT_SECRET_KEY
from modules.utils import uuid_generator

from dataclasses import dataclass

import jwt
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@dataclass
class User(database.Model):
	__tablename__ = "users"
	id:str = database.Column("id", database.String(200), nullable=False)
	username:str = database.Column("username", database.String(32), nullable=False)
	password:str = database.Column("password", database.String(128), nullable=False)
	email:str = database.Column("email", database.String(128), primary_key=True, nullable=False) # email as the primary key
	created: datetime = database.Column("created", database.DateTime, default=database.func.now())

	def testdata(self):
		user = User(username="user1", email="user@example.com", password="password")
		database.session.add(user)
		database.session.commit()

	def generate_id(self):
		self.id = uuid_generator(form="user")
		
	def generate_password(self, password):
		self.password = generate_password_hash(password)
        
	def verify_password(self, password):
		return check_password_hash(self.password, password) 
    
	def generate_auth_token(self, expiration=600):
		return jwt.encode({'id': self.id, "exp": time.time() + expiration}, JWT_SECRET_KEY, algorithm='HS256')
	
	@staticmethod
	def verify_auth_token(token):
		try:
			data = jwt.decode(token, JWT_SECRET_KEY,algorithms=['HS256'])
		except Exception as e:
			return None
		return User.query.get(data['id'])


	

        