from server import database
from dataclasses import dataclass
from server.utils import uuid_generator, v4SubNet, v6SubNet, random_v4_addr, random_v6_addr

@dataclass
class NodeInfo(database.Model):
	__tablename__ = "nodeinfo"
	id:str = database.Column("id", database.String(255), primary_key=True)
	nodename = database.Column("nodename", database.String(48), nullable=False)
	space_id: str = database.Column("space_id", database.ForeignKey("netspace.id"), nullable=False)
	v4addr:str = database.Column("v4addr", database.String(255), nullable=False)
	v6addr:str = database.Column("v6addr", database.String(255), nullable=False)
	wgaddr:str = database.Column("wgaddr", database.String(255), nullable=False)
	mtu: int = database.Column("mtu", database.Integer, nullable=False, default=1420)
	listenport: int = database.Column("listenport", database.Integer, nullable=False, default=51820)
	keepalive: int = database.Column("keepalive", database.Integer, nullable=False, default=25)
	allowedips: str = database.Column("allowedips", database.String(255), nullable=False)
	endpoint: str = database.Column("endpoint", database.String(255), nullable=True, default="")
	publickey: str = database.Column("publickey", database.String(255), nullable=True, default="")
	
	def generate_id(self, username):
		self.id = uuid_generator(form=f"node-{username}")
	
	def generate_addr(self, v4, v6, wg, v4_all, v6_all, wg_all):
		self.v4addr = random_v4_addr(network=v4) + "/24"
		self.v6addr = random_v6_addr(network=v6) + "/64"
		self.wgaddr = random_v4_addr(network=wg) + "/16"
		self.allowedips = self.v4addr[: -3] + "/32"
		if self.v4addr in v4_all or self.v6addr in v6_all or self.wgaddr in wg_all:
			self.generate_addr(v4, v6, wg, v4_all, v6_all, wg_all) 
	
	def __repr__(self):
		return "<NodeInfo(id='%s', nodename='%s', space_id='%s', v4addr='%s', v6addr='%s', wgaddr='%s', mtu='%s', listenport='%s', keepalive='%s', allowedips='%s', endpoint='%s', publickey='%s')>" % (
			self.id, self.nodename, self.space_id, self.v4addr, self.v6addr, self.wgaddr, self.mtu, self.listenport, self.keepalive, self.allowedips, self.endpoint, self.publickey)
	

@dataclass
class NetSpace(database.Model):
	__tablename__ = "netspace"
	id:str = database.Column("id", database.Integer, primary_key=True)
	user_id:str = database.Column("user_id", database.ForeignKey("users.id"), nullable=False)
	spacename = database.Column("spacename", database.String(48), primary_key=True, nullable=False)
	v4subnet:str = database.Column("v4subnet", database.String(255), nullable=False)
	v6subnet:str = database.Column("v6subnet", database.String(255), nullable=False)
	wgsubnet:str = database.Column("wgsubnet", database.String(255), nullable=False)
	nodes: NodeInfo = database.relationship("NodeInfo", backref="netspace", lazy=True)
	
	def generate_id(self):
		self.id = uuid_generator(form="netspace")
	
	def generate_subnet(self, v4_all, v6_all):
		self.v4subnet = v4SubNet()
		self.v6subnet = v6SubNet()
		self.wgsubnet = v4SubNet(intranet="link-local")
		if self.v4subnet in v4_all or self.v6subnet in v6_all:
			self.generate_subnet(v4_all, v6_all)
	
	