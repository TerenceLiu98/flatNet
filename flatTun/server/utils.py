import uuid
import string
import random
import platform
import ipaddress

def uuid_generator(form=None):
	if form == None:
		generated_uuid = str(uuid.uuid1())
	nodename = platform.node() + "-" + "".join(random.choice(string.ascii_lowercase) for i in range(4))
	generated_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://{nodename}.{form}.local"))
	return str(generated_uuid)


def v4SubNet(intranet:str=None):
    """
    A: 10.0.0.0 to 10.255.255.255
    B: 172.16.0.0 to 172.31.255.255
    C: 192.168.0.0 to 192.168.255.255
    D: 169.254.0.0 to 169.254.255.255 (link-local)
    """
    intranet_dict = ["A", "B", "C"]
    if intranet is None:
        intranet = intranet_dict[int("{}".format(random.randint(0, 2)))]
    if intranet == "A":
        ipv4 = "10.{}.{}.0/24".format(random.randint(0, 255), random.randint(0, 255))
    if intranet == "B":
        ipv4 = "172.{}.{}.0/24".format(random.randint(16, 31), random.randint(0, 255))
    if intranet == "C":
        ipv4 = "192.168.{}.0/24".format(random.randint(0, 255))
    if intranet == "link-local":
        ipv4 = "169.254.{}.0/24".format(random.randint(0, 255))
    return ipv4

def v6SubNet():
    """
    from  fd00::/64 to fdff::/64
    """ 
    ipv6 = "{:x}:{:x}:{:x}::/64".format(random.randint(0xfd00, 0xfdff),
                                        random.randint(0x1000, 0xffff),
                                        random.randint(0x1000, 0xffff))
    return ipv6

def random_v4_addr(network):
    net = ipaddress.IPv4Network(network)
    addr_no = random.randint(0, net.num_addresses)
    addr_int = int.from_bytes(net.network_address.packed, byteorder="big") + addr_no
    addr = ipaddress.IPv4Address(addr_int)
    return str(addr)

def random_v6_addr(network):
    net = ipaddress.IPv6Network(network)
    addr_no = random.randint(0, net.num_addresses)
    addr_int = int.from_bytes(net.network_address.packed, byteorder="big") + addr_no
    addr = ipaddress.IPv6Address(addr_int.to_bytes(16, byteorder="big"))
    return str(addr)