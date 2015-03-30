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


class Sandbox(cocos.layer.ColorLayer):
	is_event_handler = True
	def __init__(self):
		super( Sandbox, self ).__init__( 20,20,20,255)
		
		r = cocos.tiles.load('map1.xml')
		level1 = r['level1']

		manager = DraggableScrollingManager()
		manager.add(level1)
		self.manager = manager
		self.add(manager)

		level1.set_view(0, 0, level1.px_width, level1.px_height)
		self.current_map = level1

		menu = cocos.layer.ColorLayer(20, 20, 20, 128, 50, 50)
		menu.position = (50, 50)
		self.add(menu)

	#	self.peasant = Peasant()
	#	self.peasant.go_to_cell(level1.get_cell(1, 1))

	#	self.add(self.peasant, z=1)
	def on_mouse_press(self, x, y, buttons, modifiers):
		if buttons & pyglet.window.mouse.LEFT:
			print(self.manager.pixel_from_screen(*cocos.director.director.get_virtual_coordinates(x, y)))
			print(self.current_map.get_at_pixel(*self.manager.pixel_from_screen(*cocos.director.director.get_virtual_coordinates(x, y))))

	def on_mouse_release(self, x, y, buttons, modifiers):
		pass

		
	

if __name__ == '__main__':
	cocos.director.director.init(do_not_scale = True)
	main_scene = cocos.scene.Scene (Sandbox())
	cocos.director.director.run(main_scene)
