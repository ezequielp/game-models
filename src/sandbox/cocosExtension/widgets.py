from cocos.text import Label
import cocos.draw
import numpy as np
import pyglet
from cocos.layer import Layer 
from math import cos, sin, radians, atan2

def rotationMatrix(angle):
	angle = radians(angle)
	return np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])

rot1 = rotationMatrix(150)
rot2 = rotationMatrix(-150)

class Arrow(cocos.draw.Canvas):
	def __init__(self, start, end, color, width=1):
		super(Arrow, self).__init__()
		self.start = start
		end = np.array(end)
		start = np.array(start)
		length = float(np.linalg.norm(end-start))
		width = float(width)
		base_length = length-width


		self.p = [(width/2, 0), (width/2, base_length), (width, base_length), (0, length), (-width, base_length), (-width/2, base_length), (-width/2, 0), (width/2, 0)]

		self.color = color
		self.stroke_width = 2
		self.angle = atan2(*(end-start))

	def render(self):
		self.set_color( self.color )
		self.set_stroke_width( self.stroke_width )

		self.translate(self.start)
		self.rotate(-self.angle)
		self.move_to( self.p[0] )
		for p in self.p[1:]:
			self.line_to( p )
		
		


class SimpleWindow(Layer):
	is_event_handler = True
	def __init__(self, r, g, b, a, window_name = "Simple Window", width=None, height=None):
		super(SimpleWindow, self).__init__()

		self.widget_bar = widget_bar = WidgetBar(r, g, b, 255, window_name, width = width)
		self.contents = contents = cocos.layer.ColorLayer(r, g, b, a, width = width, height = height)
		contents.position = (0, 0)
		widget_bar.position = (0, height)

		super(SimpleWindow, self).add(contents, name = "contents")
		super(SimpleWindow, self).add(widget_bar, name = "widget_bar")
		self.moving = False
		

	def add(self, child, z=0, name=None ):
		self.contents.add(child, z, name)
		return self

	def get( self, name ):
		return self.contents.get(name)


	def remove(self, child):
		self.contents.remove(child)

	@property
	def width(self):
		return self.contents.width

	@width.setter
	def width(self, value):
		self.contents.width = value
		self.widget_bar.width = value

	@property
	def height(self):
		return self.contents.height + self.widget_bar.height

	@height.setter
	def height(self, value):
		value = max(self.widget_bar.height, value)
		self.contents.height = value
		self.widget_bar.position = (0, value)

	def on_mouse_press(self, x, y, buttons, modifiers):
		if self.widget_bar.y +self.y < y and y< self.y + self.widget_bar.y +self.widget_bar.height:
			self.moving = True
			return True

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.moving:
			self.x = self.x+dx
			self.y = self.y+dy
			return True

	def on_mouse_release(self, x, y, buttons, modifiers):
		if self.moving:
			self.moving = False
			return True


	def refresh(self):
		self.contents.on_exit()
		self.contents.on_enter()
		self.widget_bar.refresh()


class EconomyInspector(SimpleWindow):
	def __init__(self, economy, map):
		super(EconomyInspector, self).__init__(20, 20, 20, 128, width = 100, height = 100, window_name = "Economy Inspector")
		self.visible = False
		self.economy = economy
		self.map = map
		self.arrows = dict()
		self.updates = dict()
		self.colors = dict()

	def on_tile_clicked(self, tile):
		if tile and 'town_name' in tile:
			if tile['town_name'] in self.economy:
				from economy.market import Market
				market = Market((3, int(self.economy.market(tile['town_name'], "wood"))), "seed")
				inv = "\n".join("{} has {} wood".format(*x) for x in market.inventory().items()) 
				text = Label("{}\n{}".format(tile['town_name'], inv), anchor_y = "bottom", multiline = True, width=600)
				text.position = (10, 10)

				self.width = text.element.content_width+20
				self.height = text.element.content_height+20
				self.refresh()

				try:
					self.remove("text")
				except Exception, e:
					pass
				self.add(text, name = "text")
				self.visible = True

	def get_tradeables(self):
		return self.economy.total_stock.keys()

	def toggle_routes(self, tradeable, show, outgoing = False, incoming = False):
		find_params = {}
		markets = self.map.find_cells(market = True)
		markets = dict((mkt['town_name'], mkt) for mkt in markets)
		
		map(self.map.remove, self.arrows.get(tradeable, []))
		self.arrows[tradeable] = []

		if show:
			for route, source, destination in self.economy.routes():
				if source == destination:
					continue
				destination = np.array(markets[destination].center)
				source = np.array(markets[source].center)
				displacement = destination-source
				
				displacement = displacement/np.linalg.norm(displacement)
				source = source + 50*displacement
				destination = source + 100*displacement
				w = int(50*self.economy.route(route, trade = tradeable))
				if w == 0:
					continue

				arrow = Arrow(source.tolist(), destination.tolist() , self.colors.get(tradeable, (255, 255, 255, 200)), width=w)

				self.map.add(arrow)
				self.arrows[tradeable].append(arrow)
		return True

	def toggle_town_names(self, show):
		for town in self.map.find_cells(market = True):
			try:
				self.map.remove("town name " + town['town_name'])
			except:
				if show:
					title = Label(town['town_name'], anchor_x = 'center', anchor_y = "bottom")
					title.position = town.midbottom
					self.map.add(title, name="town name " + town['town_name'])

		return True

	def toggle_town_inventory(self, tradeable, show):
		for town in self.map.find_cells(market =True):
			updater_name = "tradables in " + town['town_name']
			if updater_name not in self.updates and show:
				class RefreshInventory():
					def __init__(self, economy, map, town):
						self.map = map
						self.economy = economy
						self.town = town
						self.tradeables = set()

					def __call__(self):
						layer_name = "tradeables label "+self.town['town_name']
						try:
							self.map.remove(layer_name)
						except:
							pass
						if any(self.tradeables):
							tradeables = self.economy.market(self.town['town_name']).items()
							text = "\n".join("{}: {}".format(t[0], i)  for (t, i) in tradeables if t in self.tradeables)
							tradeable_info = Label(text, width = 2*self.town.width, anchor_x = "center", anchor_y = "top", multiline = True)
							tradeable_info.position=self.town.midbottom
							self.map.add(tradeable_info, name = layer_name)

					def add_tradeable(self, tradeable):
						self.tradeables.add(tradeable)

					def remove_tradeable(self, tradeable):
						self.tradeables.remove(tradeable)

				self.updates[updater_name] = RefreshInventory(self.economy, self.map, town)


			if show:
				self.updates[updater_name].add_tradeable(tradeable)
			else:
				self.updates[updater_name].remove_tradeable(tradeable)


			self.updates[updater_name]()
				

		return True

	def update(self):
		for update in self.updates.values():
			update()


	def tradeable_color(self, tradeable, color):
		self.colors[tradeable] = tuple(list(color)+[200])

class Toggle(cocos.layer.ColorLayer):
	state = False
	colors = {False: (0, 0, 0, 128), True: (200, 200, 200, 128)}

	def __init__(self, label, on_toggle = None, width = None):
		super(Toggle, self).__init__(*self.colors[False], width = width)
		self.on_toggle = on_toggle
		
		self.label = Label(label, multiline = False, width = width, anchor_x = 'center', anchor_y = 'center')
		self.label.position = self.width/2, self.label.element.content_height/2
		self.add(self.label)
		self.height = self.label.element.content_height

	def refresh(self):
		self.label.position = self.width/2, self.label.element.content_height/2
		self.on_exit()
		self.on_enter()

	def switch(self):
		if (self.on_toggle(not self.state)):
			self.state = not self.state
			self._rgb = self.colors[self.state][0:3]
			self._opacity = self.colors[self.state][3]
			self.refresh()

class PanelTitle(Toggle):
	def __init__(self, label, width = None, color = (100, 0, 100, 128)):
		self.colors = {False: color}
		super(PanelTitle, self).__init__(label, width  = width, on_toggle = lambda state: False)
		
class WidgetBar(PanelTitle):
	def __init__(self, r, g, b, a, label, width=None):
		super(WidgetBar, self).__init__(label, width = width, color = (r, g, b, a))
		

	
class SidePanel(SimpleWindow):
	def __init__(self,  economy_inspector):
		tradeables = economy_inspector.get_tradeables()
		def createRouteToggle(tradeable):
			return Toggle(tradeable, width = 200, on_toggle = lambda state: economy_inspector.toggle_routes(tradeable, state, outgoing = True) )

		def createInventoryToggle(tradeable):
			return Toggle(tradeable, width = 200, on_toggle = lambda state: economy_inspector.toggle_town_inventory(tradeable, state))

		toggles = [createRouteToggle(tradeable) for tradeable in tradeables]
		toggles.append(PanelTitle("Show outgoing for:", width  = 200))
		toggles.extend(createInventoryToggle(tradeable) for tradeable in tradeables)
		toggles.append(PanelTitle("Show inventory of:", width  = 200))
		toggles.append(Toggle("Show town names", width  = 200, on_toggle = lambda state: economy_inspector.toggle_town_names(state)))

		height =  max(t.label.element.content_height for t in toggles)
		
		super(SidePanel, self).__init__(20, 20, 20, 128, width = 200, height = len(toggles)*height, window_name = "Display options")
		
		self.position = (cocos.director.director.window.width-200, 100)
		self.visible = True
		self.toggles = toggles
		self.toggle_height = height

		for i in range(len(toggles)): 
			toggles[i].position = (0, i*height)
			toggles[i].height = height
			self.add(toggles[i])


	def on_mouse_release(self, x, y, buttons, modifiers):
		ret = super(SidePanel, self).on_mouse_release(x, y, buttons, modifiers)
		if buttons & pyglet.window.mouse.LEFT:
			toggle = self.hit_widget(x,y)
			if toggle is not None:
				toggle.switch()
				return True
		return ret
				

	def hit_widget(self, x, y):
		w_x, w_y = self.position
		w_x1, w_y1 = self.position[0]+self.width, self.position[1]+self.height

		if not (x>w_x and x<w_x1 and y>w_y and y<w_y1):
			return None

		i = int(y-w_y)//self.toggle_height
		if i < len(self.toggles):
			return self.toggles[i]
		else:
			return None



