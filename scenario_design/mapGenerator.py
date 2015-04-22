'''
Autor: Lautaro Linquiman
Web: www.tutorialdeprogramacion.com 
Email: acc.limayyo@gmail.com
'''
from PIL import Image
class creatorMap():
	def __init__(self, srcImage, params = {}):
		'''
		srcImage: ruta de la imagen (.png)
		params{
			createHTML:0/1,
			srcDestino:(string) type xml,
			srcTemplateMap: (string) type xml
		}'''
		self.__secImage = srcImage
		self.__srcDestino = 'map.xml'
		self.__srcTemplateMap = 'template.xml'
		self.__createHTML = 0
		
		self.__xmlContent = []

		if('createHTML' in params):
			self.__createHTML = paramas['createHTML']			
		if('srcDestino' in params):
			self.__srcDestino = paramas['srcDestino']
		if('srcTemplateMap' in params):
			self.__srcTemplateMap = paramas['srcTemplateMap'] 
		
		self.image = Image.open(srcImage)		
		

	def start(self):
		for rgba in self.image.getdata():
			self.__xmlContent.append((self.__getTileNameByrgba(rgba), rgba))
		self.__createXML()
		if(self.__createHTML):
			self.__renderMapToHTML()

	def __createXML(self):
		xmlString = ''
		count = 0		
		templateStr = "\t\t\t\t<cell tile=\"tls:%s\" />\n"
		finalCount = self.image.size[0]*self.image.size[0]
		for element in self.__xmlContent:
			if((count%self.image.size[0] == 0 and not count == 0 ) or (count-1 == finalCount)):
				xmlString += "\t\t\t</column>\n"
			if(count == 0 or count%self.image.size[0] == 0):
				xmlString += "\t\t\t<column>\n"
			xmlString += templateStr % element[0]			
			count += 1
		xmlString += "\t\t\t</column>\n"
		template = open(self.__srcTemplateMap, 'r')
		contentTemplateStructure = template.read()
		template.close()
		
		parseStructure = contentTemplateStructure.replace('{xml}', xmlString)

		byTemplate = open(self.__srcDestino, 'wb')
		byTemplate.write(parseStructure)
		byTemplate.close()

	def __renderMapToHTML(self):
		pass

	def __getTileNameByrgba(self, rgba):
		''' Compara las distintas posiblidades de rgbaes para obtener el tile '''
		if(rgba[0] >= 130 and rgba[0] <= 190 and (rgba[1] <= 100 and rgba[1] > 60) and (rgba[2] <= 100 and rgba[2] > 60)):
			return 'town' #'rojoCasita'
		elif((rgba[0] > 100 and rgba[1] < 150) and rgba[0] == rgba[1] and (rgba[2] < 88)):
			return  'grass'	#verde
		elif((rgba[0] >= 60 and rgba[0] <= 130) and rgba[0] == rgba[1] and (rgba[2] >= 88 and rgba[2] <= 150)):
			return  'grass'	#verde
		elif(rgba[0] > rgba[1]):
			if(rgba[2] > rgba[0]):
				return  'water' #azul
			if(rgba[1] >= rgba[2] or rgba[1] <= rgba[2]):
				return  'arena' #rojo
		elif(rgba[1] > rgba[0]):
			if(rgba[2] > rgba[1]):
				return  'water' #azul
			elif(rgba[1] >= rgba[0] or rgba[1] <= rgba[0]):		
				return  'grass'	#verde
		elif(rgba[2] > rgba[1]):
			if(rgba[0] > rgba[2]):
				return  'arena' #rojo
			elif(rgba[1] >= rgba[0] or rgba[1] <= rgba[0]):
				return  'water' #azul

createMap = creatorMap('scenario1.png')
createMap.start()
