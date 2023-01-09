import sys
import json
import requests
import platform
import subprocess
from pathlib import Path

from utils import *

class Client(object):

	def __init__(self, url, email, password, spacename, nodename=None, nodetype=4, configpath=None, x_access_token=None) -> None:
		self.url = url
		self.email = email
		self.password = password
		self.spacename = spacename
		self.nodename = nodename if nodename != None else platform.node()
		self.nodetype = nodetype # 3 for supernode 4 for normal node 
		self.configpath = Path(__file__).resolve().parents[0] if configpath == None else configpath
		self.x_access_token = None

	def _read(self):
		with open(Path(self.configpath) / f"{self.spacename}-{self.nodename}.json", "r+") as f:
			nodeinfo = json.load(f)
			f.close()
		return nodeinfo

	def _dump(self, nodeinfo) -> str:
		with open(Path(self.configpath) / f"{self.spacename}-{self.nodename}.json", "w+") as f:
			json.dump(nodeinfo, f, indent=4)
			f.close()
		return "Dump file Scuccess"

	# login with user's email and password
	def login(self) -> str:
		url = self.url + "/api/auth/signin"
		data = {'email': self.email, 'password': self.password}
		response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
		if response.status_code == 200:
			self.x_access_token = response.headers['x-access-token']
			del self.email, self.password
			config = Path(Path(self.configpath) / f"{self.spacename}-{self.nodename}.json")
			config.touch(exist_ok=True)
			init_data = {"x-access-token": self.x_access_token, "x-client": str(4)}
			self._dump(init_data)
			return "Scuccess"
		else:
			return "Login Failed"
	
	def logout(self) -> str:
		url = self.url + "/api/auth/signout"
		nodeinfo = self._read()
		try:
			nodeinfo = self._read()
			self.x_access_token, self.x_client = nodeinfo['x-access-token'], nodeinfo['x-client']
			headers = {'x-access-token': self.x_access_token, 'x-client': self.x_client}
		except:
			raise ValueError("Please register the client first")
		response = requests.post(url, headers=headers)
		if response.status_code == 200:
			return "Scuccess"
		else:
			return "Logout Failed"
		
	# register client
	def register(self) -> str:
		url = self.url + "/api/node"
		data = {'spacename': self.spacename, 'nodename': self.nodename, 'nodetype': self.nodetype}
		try:
			nodeinfo = self._read()
			self.x_access_token, self.x_client = nodeinfo['x-access-token'], nodeinfo['x-client']
			headers = {'x-access-token': self.x_access_token, 'x-client': self.x_client}
		except:
			raise ValueError("Please register the client first")
		headers = {'x-access-token': self.x_access_token, 'x-client': self.x_client}
		response = requests.post(url, params=data, headers=headers) #FIXME: params or json?
		if response.status_code == 200:
			nodeinfo = {"nodeinfo": response.json()["data"]}
			nodeinfo["peerlist"] = {}
			nodeinfo["x-access-token"] = self.x_access_token
			self._dump(nodeinfo)
			return "Scuccess"
		else:
			return "Signup Failed"
		
	def get(self) -> str:
		url = self.url + "/api/netspace"
		try:
			nodeinfo = self._read()
			self.x_access_token, self.x_client = nodeinfo['x-access-token'], nodeinfo['nodeinfo']['role']
			headers = {'x-access-token': self.x_access_token, 'x-client': str(self.x_client)}
		except:
			raise ValueError("Please register the client first")
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			self.peerlist = response.json()["data"][0]["nodes"]
			for i in range(0, len(self.peerlist)):
				if self.peerlist[i]["id"] == nodeinfo["nodeinfo"]["id"]:
					self.peerlist.pop(i)
					break
				nodeinfo["peerlist"][self.peerlist[i]["id"]] = self.peerlist[i]
			self._dump(nodeinfo)
			return "Scuccess"
		else:
			return "Get peer Failed"
		
	def update(self) -> str:
		try:
			nodeinfo = self._read()
			self.x_access_token, self.x_client = nodeinfo['x-access-token'], nodeinfo['nodeinfo']['role']
			headers = {'x-access-token': self.x_access_token, 'x-client': str(self.x_client)}
		except:
			raise ValueError("Please register the client first")
		url = self.url + "/api/node"
		data = {"spacename": self.spacename, "nodename":self.nodename}
		if nodeinfo["nodeinfo"]["publickey"] == "":
			nodeinfo["nodeinfo"]["privatekey"], nodeinfo["nodeinfo"]["publickey"] = genkey()
		self._dump(nodeinfo)
		nodeinfo["nodeinfo"].pop("privatekey")
		response = requests.put(url, params=data, json=nodeinfo["nodeinfo"], headers=headers)
		if response.status_code == 200:
			return "Scuccess"
		else:
			return "Update nodeinfo Failed"	

	def withdraw(self) -> str:
		try:
			nodeinfo = self._read()
			self.x_access_token, self.x_client = nodeinfo['x-access-token'], nodeinfo['nodeinfo']['role']
			headers = {'x-access-token': self.x_access_token, 'x-client': str(self.x_client)}
		except:
			raise ValueError("Please register the client first")
		url = self.url + "/api/node"
		data = {'spacename': self.spacename, 'nodename': self.nodename}
		response = requests.delete(url, params=data, headers=headers)
		if response.status_code == 200:
			print("With draw Scuccess, bye!")
			sys.exit(0)
		else:
			return "Withdraw Failed"
		
	def parse(self) -> str:
		try:
			nodeinfo = self._read()
		except:
			raise ValueError("Please register the client first")
		
		#parse interface 
		peerlist = list(nodeinfo["peerlist"].keys())
		nodeinfo_ = nodeinfo["nodeinfo"]
		fdb_statement = ""
		for i in range(0, len(peerlist)):
			peer = nodeinfo["peerlist"][peerlist[i]]
			fdb_statement += f"bridge fdb append to 00:00:00:00:00:00 dst {peer['wgaddr']} dev v%i\n"
			
		interface = "[Interface]\n" + \
					f"Address = {nodeinfo_['wgaddr']}\n" + \
					f"PrivateKey = {nodeinfo_['privatekey']}\n" + \
					f"ListenPort = {nodeinfo_['listenport']}\n" + \
					f"MTU = {nodeinfo_['mtu']}\n" + \
					"Table =off \n" + \
					"# PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; iptables -A FORWARD -i eth0 -o v%i -m state --state RELATED,ESTABLISHED -j ACCEPT; iptables -A FORWARD -i v%i -o eth0 -j ACCEPT; ip route add\n" + \
					"# PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; iptables -D FORWARD -i eth0 -o v%i -m state --state RELATED,ESTABLISHED -j ACCEPT; iptables -D FORWARD -i v%i -o eth0 -j ACCEPT; ip route del\n" + \
					fdb_statement + \
					f"PostUp = ip address add  dev %i {nodeinfo_['v4addr']} \n" + \
					f"PostUp = ip address add  dev %i {nodeinfo_['v6addr']} \n" + \
					"PostUp = ip link set dev %i up \n" + \
					"PreDown = ip link set dev %i down \n" + \
					"PreDown = ip link delete dev %i \n"		
		#parse peer
		for i in range(0, len(peerlist)):
			peer = nodeinfo["peerlist"][peerlist[i]]
			interface += f"\n[Peer]\n" + \
						f"PublicKey = {peer['publickey']}\n" + \
						f"AllowedIPs = {peer['wgaddr']}\n" + \
						f"Endpoint = {peer['endpoint']}\n" + \
						f"PersistentKeepalive = {peer['keepalive']}\n"
		
		with open(Path(self.configpath) / f"{self.spacename}-{self.nodename}.conf", "w") as f:
			f.write(interface)
			f.write("\n")
			f.close()
		return "Scuccess"
			
	def wg(self, command):
		try:
			nodeinfo = self._read()
		except:
			raise ValueError("Please register the client first")
		if command == "up":
			try:
				proc = subprocess.Popen(f"wg-quick up /{self.configpath}/{self.spacename}-{self.nodename}.conf", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
			except:
				raise ValueError(f"Output:{out}\n Error: {err}")
		elif command == "down":
			try:
				proc = subprocess.Popen(f"wg-quick down /{self.configpath}/{self.spacename}-{self.nodename}.conf", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
			except:
				raise ValueError(f"Output:{out}\n Error: {err}")
		elif command == "status":
			try:
				proc = subprocess.Popen(f"wg show {self.spacename}-{self.nodename}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
			except:
				raise ValueError(f"Output:{out}\n Error: {err}")
		elif command == "restart":
			try:
				proc = subprocess.Popen(f"wg-quick down /{self.configpath}/{self.spacename}-{self.nodename}.conf", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
				proc = subprocess.Popen(f"wg-quick up /{self.configpath}/{self.spacename}-{self.nodename}.conf", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
			except:
				raise ValueError(f"Output:{out}\n Error: {err}")
		

	

		
		