import uuid
import string
import random
import platform

def uuid_generator(form=None):
	if form == None:
		generated_uuid = str(uuid.uuid1())
	hostname = platform.node() + "-" + "".join(random.choice(string.ascii_lowercase) for i in range(4))
	generated_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://{hostname}.{form}.local"))
	return str(generated_uuid)