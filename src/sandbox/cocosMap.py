import cocosExtension.tiles as newtiles
import cocos, pyglet, numpy

cocos.tiles.Resource.register_factory('regularhexmap')(newtiles.wesnoth_hexmap_factory)

#class Peasant(cocos.sprite.Sprite):
#	def __init__(self):
#		super( Peasant, self).__init__("assets/peasant.png")
#
#	def go_to_cell(self, cell):
#		self.position = cell.center
class DraggableScrollingManager(cocos.layer.ScrollingManager):
	is_event_handler = True
	def __init__(self):
		super(DraggableScrollingManager, self).__init__()

		self.start_drag = None
		self.start_focus = None

	def on_mouse_release(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			self.start_drag = None
			self.start_focus = None

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			if not self.start_drag:
				self.start_drag = (x, y)
				self.start_focus = self.restricted_fx, self.restricted_fy
			
			self.set_focus(self.start_focus[0]+self.start_drag[0]-x, self.start_focus[1]+self.start_drag[1]-y)


class Sandbox(cocos.layer.ColorLayer, pyglet.event.EventDispatcher):
	is_event_handler = True
	def __init__(self, mapFile):
		super( Sandbox, self ).__init__( 20,20,20,255)
		
		r = cocos.tiles.load(mapFile)
		level1 = r['level1']

		manager = DraggableScrollingManager()
		manager.add(level1)
		self.manager = manager
		self.add(manager)

		#level1.set_view(0, 0, level1.px_width, level1.px_height)
		self.current_map = level1

	def get_tile_at_virtual_coord(self, x, y):
		return self.current_map.get_at_pixel(*self.manager.pixel_from_screen(*cocos.director.director.get_virtual_coordinates(x, y)))

	def on_mouse_press(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			self.clicked = self.get_tile_at_virtual_coord(x, y)
			
	def on_mouse_release(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT & (self.clicked == self.get_tile_at_virtual_coord(x, y)):
			clicked, self.clicked = self.clicked, None
			self.dispatch_event('on_tile_clicked', clicked)

	def toggle_town_names(self, show):
		for town in self.current_map.find_cells(market = True):
			try:
				self.current_map.remove("town name " + town['town_name'])
			except:
				if show:
					title = Label(town['town_name'], anchor_x = 'center', anchor_y = "top")
					title.position = town.midbottom
					self.current_map.add(title, name="town name " + town['town_name'])

		return True

Sandbox.register_event_type('on_tile_clicked')
from cocos.text import Label

class EconomyInspector(cocos.layer.ColorLayer):
	def __init__(self, economy):
		super(EconomyInspector, self).__init__(20, 20, 20, 128, width = 100, height = 100)
		self.visible = False
		self.economy = economy

	def on_tile_clicked(self, tile):
		if 'town_name' in tile:
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
					print(e)
					pass
				self.add(text, name = "text")
				self.visible = True

	def refresh(self):
		self.on_exit()
		self.on_enter()

class Toggle(cocos.layer.ColorLayer):
	state = False
	colors = {False: (0, 0, 0, 128), True: (200, 200, 200, 128)}

	def __init__(self, label, on_toggle = None, width = None):
		super(Toggle, self).__init__(*self.colors[False], width = width)
		self.on_toggle = on_toggle
		
		self.label = Label(label, multiline = False, width = width, anchor_x = 'center', anchor_y = 'center')
		self.label.position = self.width/2, self.label.element.content_height/2
		self.add(self.label)

	

	def refresh(self):
		self.on_exit()
		self.on_enter()

	def switch(self):
		if (self.on_toggle(not self.state)):
			self.state = not self.state
			self._rgb = self.colors[self.state][0:3]
			self._opacity = self.colors[self.state][3]
			self.refresh()


class SidePanel(cocos.layer.ColorLayer):
	is_event_handler = True
	def __init__(self, economy, sandbox):
		self.economy = economy

		tradeables = economy.total_stock.keys()

		toggles = [Toggle(tradeable, width = 200, on_toggle = lambda state: self.show_routes(tradeable, state) ) for tradeable in tradeables] + \
			[Toggle("Show town names", width  = 200, on_toggle = lambda state: sandbox.toggle_town_names(state))]

		height =  max(t.label.element.content_height for t in toggles)
		
		super(SidePanel, self).__init__(20, 20, 20, 128, width = 200, height = len(toggles)*height)
		
		self.position = (cocos.director.director.window.width-200, 100)
		self.visible = True
		self.toggles = toggles
		self.toggle_height = height

		for i in range(len(toggles)): 
			toggles[i].position = (0, i*height)
			toggles[i].height = height
			self.add(toggles[i])

	def on_mouse_release(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			toggle = self.hit_widget(*cocos.director.director.get_virtual_coordinates(x, y))
			if toggle is not None:
				toggle.switch()
				

	def hit_widget(self, x, y):
		w_x, w_y = self.position
		w_x1, w_y1 = self.position[0]+self.width, self.position[1]+self.height

		if not (x>w_x and x<w_x1 and y>w_y and y<w_y1):
			return None

		i = int(y-w_y)//self.toggle_height

		return self.toggles[i]

	def show_routes(self, tradeable, new_state):
		print("switch ", tradeable, new_state)
		return True


	def refresh(self):
		self.on_exit()
		self.on_enter()


if __name__ == '__main__':
	import sys
	sys.path.append('..')

	from economy import economy

	e = economy.Economy(('wood',))

	e.add_market('town a', wood = 20)
	e.add_market('town b', wood = 30)
	e.add_market('town c', wood = 10)

	e.add_route('a-b path', source="town a", to = "town b", traffic = (0.3,))
	e.add_route('town a self', source="town a", to = "town a", traffic = (0.3,))
	e.add_route('a-c path', source="town a", to = "town c", traffic = ('rest',))
	e.add_route('b-c smuggle', source="town b", to = "town c", traffic = (0.1,))
	e.add_route('town b self', source="town b", to = "town b", traffic = ("rest",))
	e.add_route('town c self', source="town c", to = "town c", traffic = ("rest",))


	cocos.director.director.init(do_not_scale = True)

	sbx = Sandbox('map1.xml')
	h = EconomyInspector(e)
	sp = SidePanel(e, sbx)

	h.position = (0, 50)
	sbx.push_handlers(h)


	main_scene = cocos.scene.Scene (sbx, h, sp)
	main_scene.schedule_interval(lambda x: e.step(), 10)

	cocos.director.director.run(main_scene)

