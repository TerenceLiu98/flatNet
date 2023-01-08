from server import database
from dataclasses import dataclass


@dataclass
class TokensBlacklist(database.Model):
	__tablename__ = "tokensblacklist"
	id:str = database.Column("id", database.Integer, primary_key=True)
	expired_token:str = database.Column("expired_token", database.String(255), nullable=False)
    
	def __repr__(self):
		return "<Tokens(id='%s',  expired_token='%s', status='invalid')>" % (
			self.id, self.expired_token)