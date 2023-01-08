from modules import *
from modules.auth.api import SignIn, SignOut, SignUp, UserToken, Resources


routes = Blueprint("auth", __name__)
auth_api = Api(routes)
auth_api.add_resource(SignIn, "/api/auth/signin")
auth_api.add_resource(SignOut, "/api/auth/signout")
auth_api.add_resource(SignUp, "/api/auth/signup")
auth_api.add_resource(UserToken, "/api/auth/refresh")
auth_api.add_resource(Resources, "/api/auth/resources")