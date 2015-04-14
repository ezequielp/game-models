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

if __name__ == '__main__':
	import sys
	sys.path.append('..')

	from economy import economy

	e = economy.Economy(('wood', 'ore'))

	e.add_market('town a', wood = 200, ore = 100)
	e.add_market('town b', wood = 300, ore = 150)
	e.add_market('town c', wood = 100, ore = 500)

	e.add_route('town a self', source="town a", destination = "town a", traffic = (0.3,0.8))
	e.add_route('a-b path', source="town a", destination = "town b", traffic = (0.3,0.1))
	e.add_route('a-c path', source="town a", destination = "town c", traffic = ('rest','rest'))

	e.add_route('b-c smuggle', source="town b", destination = "town c", traffic = (0.1,0.0))
	e.add_route('b-a path', source="town b", destination = "town a", traffic = (0.1,0.9))
	e.add_route('town b self', source="town b", destination = "town b", traffic = ("rest","rest"))

	e.add_route('town c self', source="town c", destination = "town c", traffic = ("rest","rest"))


	cocos.director.director.init(do_not_scale = True)

	sbx = Sandbox('map1.xml')

	#Widgets
	from cocosExtension.widgets import EconomyInspector, SidePanel

	h = EconomyInspector(e, sbx.current_map)
	sp = SidePanel(h)

	h.position = (0, 50)
	h.tradeable_color('ore', (255, 0, 0))
	h.tradeable_color('wood', (0, 0, 255))

	sbx.push_handlers(h)


	main_scene = cocos.scene.Scene (sbx, h, sp)
	def update():
		e.step()
		h.update()

	main_scene.schedule_interval(lambda x: update(), 2)

	cocos.director.director.run(main_scene)
