from server import *
from server.auth.api import SignIn, SignOut, SignUp, TokenRefresh


routes = Blueprint("auth", __name__)
auth_api = Api(routes)
auth_api.add_resource(SignIn, "/api/auth/signin")
auth_api.add_resource(SignOut, "/api/auth/signout")
auth_api.add_resource(SignUp, "/api/auth/signup")
auth_api.add_resource(TokenRefresh, "/api/auth/refresh")