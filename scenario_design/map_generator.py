'''
Autor: Lautaro Linquiman
Web: www.tutorialdeprogramacion.com 
Email: acc.limayyo@gmail.com
Version: 0.2
'''
from __future__ import division
import sys
from colorsys import rgb_to_hls

try:
    from PIL import Image
except ImportError:
    print 'Tienes que instalar la libreria PIL'
    print 'pip install PIL o en http://www.pythonware.com/products/pil/'
    sys.exit()

def rgb_to_hls_int(rgb):
    ''' Tranforma los valores de rgb_to_hls a grados enteros'''
    red, green, blue = rgb[0:3]
    hue, lightness, saturation = rgb_to_hls(red/255, green/255, blue/255)

    return (round(hue*360), round(lightness*100), round(saturation*100))




class ImageToMap():

    def __init__(
        self, src_image, output_file_base = 'map', 
        xml_template = 'template.xml', html_template = 'template.html', 
        verbose = False):
        '''Constructor

        Args:
            src_image (str): Name of source image
            output_file_base (str, optional): Base name of output files (without extension)
            xml_template (str, optional): Template file to create xml from
            html_template (str, optional): Template file to create html from
        '''
        self.__src_destino = output_file_base
        self.__src_template_map = xml_template
        self.__src_html_template = html_template
        self.file_content = ""
        self.pixel_count = 0
        self.__xml_content = []
        self.verbose = verbose

        self.image = Image.open(src_image)       
        self.img_size = self.image.size[0]

    def start(self, create_html = False, write_log = True):
        """
        Start image transformation
        
        Args:
            create_html (bool, optional): Output html file
            write_log (bool, optional): Output log file
        """
        for rgba in self.image.getdata():
            self.__xml_content.append(self.__get_tile_name_by_rgba(rgba, write_log))

        self.__create_xml()

        if write_log:
            self.print_log('creando log')
            with open('log.txt','wb') as log_file:
                log_file.write(self.file_content)
            self.print_log('log creado')

        if create_html:
            self.__render_map_to_html()

    def print_log(self, text):
        """Outputs a log string
        
        Args:
            text (string): Sentence to log
        """
        if self.verbose:
            print text.center(50,'-')

    def __create_xml(self):
        """
        Write image data to XML
        """
        self.print_log('creando mapa...')
        xml_string = ''
        count = 0       
        template_str = "\t\t\t\t<cell tile=\"tls:%s\" />\n"
        final_count = self.img_size*self.img_size

        for element in self.__xml_content:
            if((count%self.img_size == 0 and not count == 0 ) 
                or (count == final_count)):
                xml_string += "\t\t\t</column>\n"
            if(count == 0 or count%self.img_size == 0):
                xml_string += "\t\t\t<column>\n"
            xml_string += template_str % element         
            count += 1

        xml_string += "\t\t\t</column>\n"
        with open(self.__src_template_map, 'r') as template:
            xml_template = template.read()
        
        parse_structure = xml_template.replace('{xml}', xml_string)
        with open(self.__src_destino+'.xml', 'wb') as by_template:
            by_template.write(parse_structure)
        
        self.print_log('%s creado correctamente' % (self.__src_destino+'.xml'))
        

    def __render_map_to_html(self):
        """
        Write image data to HTML
        """
        self.print_log('creando mapa html')
        html = ""
        with open(self.__src_html_template, 'r') as template:
            html_template = template.read()

        count = 0
        for tile in self.__xml_content:
            count += 1
            tile_util = tile
            color = ''
            if tile_util == 'arena':
                color = 'red'
            elif tile_util == 'grass':
                color = 'green'
            elif tile_util == 'water':
                color = 'blue'
            html += html_template % (color, count, tile)
            if count % self.img_size == 0:
                html += "<div style='clear:both'></div>"
                
        with open(self.__src_destino+'.html', 'wb') as html_file:
            html_file.write(html)
        
        self.print_log('%s creado correctamente' % (self.__src_destino+'.html'))
        
    def __get_tile_name_by_rgba(self, rgba, write_log = False):
        """
        Compares different hls values to obtain the tile name
        """
        hls_color = rgb_to_hls_int(rgba)
        hls_util_color = hls_color[0]
        if write_log:
            self.pixel_count += 1
            self.file_content += "Pixel %d value %d %d %d \n" % (
                self.pixel_count, 
                hls_color[0], hls_color[1], hls_color[2])
        if(hls_util_color < 120):
            #Color rojo
            return 'arena'
        elif(hls_util_color >= 120 and 150 > hls_util_color):
            #color verde
            return 'grass'
        elif(hls_util_color >= 150):
            #color azul
            return 'water'      

if __name__ == '__main__':
    create_map = ImageToMap('scenario1.png', output_file_base = 'map2', verbose = True)
    create_map.start(create_html = True)
