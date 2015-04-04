import cocosExtension.tiles as newtiles
import cocos, pyglet

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

Sandbox.register_event_type('on_tile_clicked')

class EconomyInspector(object):
	def __init__(self, view, economy):

		view.push_handlers(self)

		self.view = view
		self.economy = economy

	def on_tile_clicked(self, tile):
		if 'town_name' in tile:
			if tile['town_name'] in self.economy:
				from economy.market import Market
				from cocos.text import Label

				market = Market((3, int(self.economy.market(tile['town_name'], "wood"))), "seed")

				inv = "\n".join("{} has {} wood".format(*x) for x in market.inventory().items()) 
				
				text = Label("{}\n{}".format(tile['town_name'], inv), anchor_y = "bottom", multiline = True, width=600)
				text.position = (10, 10)
				
				text_area = cocos.layer.ColorLayer(20, 20, 20, 128, text.element.content_width+20, text.element.content_height+20)
				text_area.position = (50, 50)
				text_area.add(text)

				try:
					self.view.remove("debug_box")
				except Exception, e:
					pass
				self.view.add(text_area, name = "debug_box")


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


	main_scene = cocos.scene.Scene (sbx)
	main_scene.schedule_interval(lambda x: e.step(), 10)

	


	h = EconomyInspector(sbx, e)

	cocos.director.director.run(main_scene)

