import re
import yaml

def tuple_constructor(loader, node):
	value = loader.construct_scalar(node)
	return tuple(map(int, value[1:-1].split(',')))

class WorldFactoryYaml():
	def __init__(self, config):
		yaml.add_constructor(u'!position', tuple_constructor)

		match_tuple = re.compile(r'^\(\d\ *, *\d\)$')
		yaml.add_implicit_resolver(u'!position', match_tuple)
		
		self.parsed_file = yaml.load(config)

		#Convert map to xml
		...
		#Replace tiles with cities
		...
		#Create Economy object
		...

	def getMapXml(self):
		pass

	def getEconomy(self):
		pass

if __name__ == '__main__':
	with file('scenario1.yaml') as f:
		print yaml.dump(WorldFactoryYaml(f).parsed_file)