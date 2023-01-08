import argparse
from client import *

def main():
	parser = argparse.ArgumentParser(description='flatTun client')
	parser.add_argument('-u', '--url', type=str, default="http://localhost:5000", help='flatTun server url')
	parser.add_argument('-e', '--email', type=str, default="admin@localhost", help='flatTun server email address')
	parser.add_argument('-p', '--password', type=str, default="admin", help='flatTun server password')
	parser.add_argument('-s', '--spacename', type=str, default="default", help='flatTun server spacename')
	parser.add_argument('-n', '--nodename', type=str, default=None, help='flatTun server nodename')
	parser.add_argument('-f', '--file', type=str, default=None, help='flatTun configuration file absolute location')
	parser.add_argument('-c', '--command', type=str, default="login", help='flatTun command')
	return parser

def print_help(program_name: str) -> None:
    print('Usage vwgen <cmd> [<args>]')
    print()
    print('### Required arguments ###')
    print('  -u, --url: flatTun server url')
    print('  -e, --email: flatTun user email address, ofter login, th email address will be deleted')
    print('  -p, --password: flatTun user password, ofter login, th password will be deleted')
    print('  -s, --spacename: flatTun spacename')
    print('### Optional arguments ###')
    print('  -n, --nodename: flatTun nodename')
    print('  -f, --file: flatTun configuration file absolute location')
    print('  -c, --command: flatTun command')
    print("You may pass '--help' to any of these subcommands to view usage.")

if __name__ == "__main__":
	
	parser = main()
	if len(sys.argv) < 2 or sys.argv[1] == '--help':
		print_help(sys.argv[0])
		sys.exit(1)
		
	args = parser.parse_args()
	client = Client(url=args.url, email=args.email, password=args.password, spacename=args.spacename, nodename=args.nodename)
	if args.command == "login":
		print(f"{args.command}: {client.login()}")
	elif args.command == "logout":
		print(f"{args.command}: {client.logout()}")
	elif args.command == "register":
		print(f"{args.command}: {client.register()}")
	elif args.command == "get":
		print(f"{args.command}: {client.get()}")
	elif args.command == "update":
		print(f"{args.command}: {client.update()}")
	elif args.command == "parse":
		print(f"{args.command}: {client.parse()}")
		
	


	