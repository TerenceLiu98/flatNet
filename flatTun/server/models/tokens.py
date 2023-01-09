from server import database
from dataclasses import dataclass

@dataclass
class TokensBlacklist(database.Model):
	__tablename__ = "tokensblacklist"
	id:str = database.Column("id", database.Integer, primary_key=True)
	#role: str = database.Column("role", database.String(8), nullable=False)
	expired_token:str = database.Column("expired_token", database.String(255), nullable=False)
    
	def __repr__(self):
		return "<Tokens(id='%s',  expired_token='%s', role='%s', status='invalid')>" % (
			self.id, self.role, self.expired_token)