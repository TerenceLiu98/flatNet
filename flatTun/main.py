from modules import init_app, database
from modules.models.users import User as UserModel

app = init_app()

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0")