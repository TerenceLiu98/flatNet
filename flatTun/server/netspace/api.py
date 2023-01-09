from server import *
from server.config import JWT_SECRET_KEY
from server.models.users import User as UserModel
from server.models.tokens import TokensBlacklist as TokensBlacklistModel
from server.models.netspace import NodeInfo as NodeInfoModel, NetSpace as NetSpaceModel

from server.auth.utils import token_required, token_required_role

class NetSpace(Resource):
	@staticmethod
	@token_required_role(['user', 'supernode', 'node'])
	def get(current_user):
		# Get all NetSapce with user.id
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id).all()
		if not netspace:
			response = make_response(jsonify(message='No NetSpace found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		ip_addr = request.remote_addr
		user_agent = request.user_agent
		response = make_response(jsonify(message='success', data=netspace), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response
	
	@staticmethod
	@token_required_role(['user'])
	def post(current_user):
		spacename = request.args.get("spacename")
		if spacename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		if NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first() is not None:
			response = make_response(jsonify(message='NetSpace already exists'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		netspace_all = NetSpaceModel.query.filter_by(user_id=current_user.id).all()
		v4_all, v6_all = [netspace.v4subnet for netspace in netspace_all], [netspace.v6subnet for netspace in netspace_all]
		netspace = NetSpaceModel(spacename=spacename, user_id=current_user.id)
		netspace.generate_id()
		netspace.generate_subnet(v4_all, v6_all)
		database.session.add(netspace)
		database.session.commit()
		response = make_response(jsonify(message='success', data=netspace), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response
	
	@staticmethod
	@token_required_role(['user'])
	def delete(current_user):
		spacename = request.args.get("spacename")
		if spacename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first()
		if netspace is None:
			response = make_response(jsonify(message='NetSpace not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		database.session.delete(netspace)
		database.session.commit()
		response = make_response(jsonify(message='success', data=netspace.spacename), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response
		

class NodeInfo(Resource):
	@staticmethod
	@token_required_role(["user", "supernode", "node"])
	def get(current_user):
		# Get peers with user.id and netspace name
		spacename = request.args.get("spacename")
		if spacename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first()
		if netspace is None:
			response = make_response(jsonify(message='NetSpace not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		nodeinfo = NodeInfoModel.query.filter_by(space_id=netspace.id).all()
		response = make_response(jsonify(message='success', data=nodeinfo), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response
	
	@staticmethod
	@token_required_role(["user", "supernode", "node"])
	def put(current_user):
		nodename = request.args.get("nodename")
		spacename = request.args.get("spacename")
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first()
		if nodename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		if netspace is None:
			response = make_response(jsonify(message='NetSpace not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		nodeinfo = NodeInfoModel.query.filter_by(space_id=netspace.id, nodename=nodename).first()
		if nodeinfo is None:
			response = make_response(jsonify(message='NodeInfo not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		nodeinfo = NodeInfoModel.query.filter(NodeInfoModel.space_id==netspace.id, NodeInfoModel.nodename==nodename)
		nodeinfo.update(dict(request.json))
		database.session.commit()
		response = make_response(jsonify(message='success', data=request.json), 200)
		return response
	
	@staticmethod
	@token_required_role(["user", "supernode", "node"])
	def post(current_user):
		nodename = request.args.get("nodename")
		spacename = request.args.get("spacename")
		role = request.args.get("nodetype")
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first()
		if nodename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		if netspace is None:
			response = make_response(jsonify(message='NetSpace not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		if NodeInfoModel.query.filter_by(space_id=netspace.id, nodename=nodename).first() is not None:
			response = make_response(jsonify(message='NodeInfo already exists'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		node_all = NodeInfoModel.query.filter_by(space_id=netspace.id).all()
		v4_all, v6_all, wg_all = [node.v4addr for node in node_all], [node.v6addr for node in node_all], [node.wgaddr for node in node_all]
		nodeinfo = NodeInfoModel(nodename=nodename, space_id=netspace.id)
		nodeinfo.generate_id(username=current_user.username)
		nodeinfo.generate_addr(v4=netspace.v4subnet, v6=netspace.v6subnet, wg=netspace.wgsubnet,
						v4_all=v4_all, v6_all=v6_all, wg_all=wg_all)
		nodeinfo.assign_role(role=role)
		database.session.add(nodeinfo)
		database.session.commit()
		response = make_response(jsonify(message='success', data=nodeinfo), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response
		
	@staticmethod
	@token_required_role(["user", "supernode", "node"])
	def delete(current_user):
		nodename = request.args.get("nodename")
		spacename = request.args.get("spacename")
		netspace = NetSpaceModel.query.filter_by(user_id=current_user.id, spacename=spacename).first()
		if nodename is None:
			response = make_response(jsonify(message='Missing arguments'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		if netspace is None:
			response = make_response(jsonify(message='NetSpace not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		nodeinfo = NodeInfoModel.query.filter_by(space_id=netspace.id, nodename=nodename).first()
		if nodeinfo is None:
			response = make_response(jsonify(message='NodeInfo not found'), 400)
			response.headers['x-access-token'] = request.headers['x-access-token']
			return response
		database.session.delete(nodeinfo)
		database.session.commit()
		response = make_response(jsonify(message='success', data=nodeinfo.nodename), 200)
		response.headers['x-access-token'] = request.headers['x-access-token']
		return response