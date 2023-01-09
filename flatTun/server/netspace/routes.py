from server import Blueprint, Api
from server.netspace.api import NetSpace, NodeInfo


routes = Blueprint("netspace", __name__)
netspace_api = Api(routes)
netspace_api.add_resource(NodeInfo, "/api/node")
netspace_api.add_resource(NetSpace, "/api/netspace")