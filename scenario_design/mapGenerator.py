'''
Autor: Lautaro Linquiman
Web: www.tutorialdeprogramacion.com 
Email: acc.limayyo@gmail.com
Version: 0.2
'''
from __future__ import division
from sys import exit
from colorsys import rgb_to_hls

try:
	from PIL import Image
except ImportError:
	print 'Tienes que instalar la libreria PIL'
	print 'pip install PIL o en http://www.pythonware.com/products/pil/'
	exit()

def rgbToHls(rgb):
	''' Tranforma los valores de rgb_to_hls a grados enteros'''
	r,g,b = rgb[0:3]
	h,l,s = rgb_to_hls(r/255,g/255,b/255)
	listReturn = (round(h*360), round(l*100), round(s*100))
	return listReturn

class creatorMap():
	def __init__(self, srcImage, params = {}):
		'''
		srcImage: ruta de la imagen (.png)
		params{
			createHTML:{default 0}/1 Crea un archivo html con la configuracion del mapa
			createLog:0/{default 1} Crea un log con la informacion de cada px
			srcDestino:(string) archivo de destino del mapa {default map}
			srcTemplateMap: (string) template para generar el mapa, es necesario que tenga el atributo {xml} {default template.xml}
			
		}'''
		self.__secImage = srcImage
		self.__srcDestino = 'map'
		self.__srcTemplateMap = 'template.xml'
		self.__createHTML = 0
		self.__createLog = 1
		self.fileContent = ""
		self.pixelCount = 0
		self.__xmlContent = []

		if('createHTML' in params):
			self.__createHTML = params['createHTML']			
		if('srcDestino' in params):
			self.__srcDestino = params['srcDestino']
		if('srcTemplateMap' in params):
			self.__srcTemplateMap = params['srcTemplateMap'] 
		if('createLog' in params):
			self.__createLog = params['createLog']
		self.image = Image.open(srcImage)		
		self.imgSize = self.image.size[0]

	def start(self):
		for rgba in self.image.getdata():
			self.__xmlContent.append((self.__getTileNameByrgba(rgba),))
		self.__createXML()
		if(self.__createLog):
			print 'creando log'.center(50,'-')
			f=open('log.txt','wb')
			f.write(self.fileContent)
			f.close()
			print 'log creado'.center(50,'-')
		if(self.__createHTML):
			self.__renderMapToHTML()

	def __createXML(self):
		print 'creando mapa...'.center(50,'-')
		xmlString = ''
		count = 0		
		templateStr = "\t\t\t\t<cell tile=\"tls:%s\" />\n"
		finalCount = self.imgSize*self.imgSize
		for element in self.__xmlContent:
			if((count%self.imgSize == 0 and not count == 0 ) 
				or (count == finalCount)):
				xmlString += "\t\t\t</column>\n"
			if(count == 0 or count%self.imgSize == 0):
				xmlString += "\t\t\t<column>\n"
			xmlString += templateStr % element[0]			
			count += 1
		xmlString += "\t\t\t</column>\n"
		template = open(self.__srcTemplateMap, 'r')
		contentTemplateStructure = template.read()
		template.close()		
		parseStructure = contentTemplateStructure.replace('{xml}', xmlString)
		byTemplate = open(self.__srcDestino+'.xml', 'wb')
		byTemplate.write(parseStructure)
		byTemplate.close()		
		print ('%s creado correctamente' % (self.__srcDestino+'.xml')).center(50,'-')
		

	def __renderMapToHTML(self):
		print 'creando mapa html'.center(50,'-')
		html = ""
		templateDivHtml = "<div style='background-color:%s; width:10px; height:10px;float:left' title='%d %s'></div>"
		count = 0
		for tile in self.__xmlContent:
			count += 1
			tileUtil = tile[0]
			color = ''
			if tileUtil == 'arena':
				color = 'red'
			elif tileUtil == 'grass':
				color = 'green'
			elif tileUtil == 'water':
				color = 'blue'
			html += templateDivHtml % (color,count,tile)
			if count%self.imgSize == 0:
				html += "<div style='clear:both'></div>"
				
		htmlFile = open(self.__srcDestino+'.html', 'wb')
		htmlFile.write(html)
		htmlFile.close()
		print ('%s creado correctamente' % (self.__srcDestino+'.html')).center(50,'-')
		
	def __getTileNameByrgba(self, rgba):
		#'''Compara los distintos valores hls para obtener el tile'''
		hlsColor = rgbToHls(rgba)
		hlsUtilColor = hlsColor[0]
		if(self.__createLog):
			self.pixelCount += 1
			self.fileContent += "Pixel %d value %d %d %d \n" % (self.pixelCount, hlsColor[0], hlsColor[1], hlsColor[2])
		if(hlsUtilColor < 120):
			#Color rojo
			return 'arena'
		elif(hlsUtilColor >= 120 and 150 > hlsUtilColor):
			#color verde
			return 'grass'
		elif(hlsUtilColor >= 150):
			#color azul
			return 'water'		

createMap = creatorMap('scenario1.png',{'createHTML': 1, 'srcDestino': 'map2'})
createMap.start()
