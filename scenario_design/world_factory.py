import re
from map_generator import ImageToMap
import xml.etree.ElementTree as ET
try:
    import yaml
except ImportError:
    raise Exception("yaml not found. Install using:\npip install PyYAML")

def tuple_constructor(loader, node):
    """Parse yaml node to extract a tuple
    
    Returns:
        tuple: Parsed tuple
    """
    value = loader.construct_scalar(node)
    return tuple(int(coord) for coord in value[1:-1].split(','))

class WorldFactoryYaml():
    """
    Parses config file and generates defined objects
    """
    def __init__(self, config):
        yaml.add_constructor(u'!position', tuple_constructor)

        match_tuple = re.compile(r'^\(\d+\ *, *\d+\)$')
        yaml.add_implicit_resolver(u'!position', match_tuple)
        
        parsed_file = yaml.load(config)

        #Convert map to xml
        map_generator = ImageToMap(parsed_file['terrain'])
        xml = ET.fromstring(map_generator.as_xml())

        #Replace tiles with cities
        cell_xpath = "regularhexmap/column[{}]/cell[{}]"
        for city in parsed_file['cities']:
            column, row = city['position']
            cell = xml.find(cell_xpath.format(column, row))
            cell.set('tile', 'tls:city')
            for config_name, xml_name in [("name", "town_name")]:
                if config_name in city:
                    attrib = {
                        'name': xml_name, 
                        'value': city[config_name]}
                    cell.append(ET.Element('property', attrib = attrib))

        #Create Economy object
        self.xml = xml

    def get_map_xml(self):
        """Return map parsed from config's terrain with added cities.
        
        Returns:
            str: xml map
        """
        return ET.tostring(self.xml, encoding='utf8', method='xml')

    def get_economy(self):
        """Return Economy object created from config file
        
        Returns:
            Economy: Economy object
        """
        pass

if __name__ == '__main__':
    with file('scenario1.yaml') as f:
        WorldFactoryYaml(f)