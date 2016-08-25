import cocosExtension.tiles as newtiles
import cocos
import pyglet

cocos.tiles.Resource.register_factory('regularhexmap')(newtiles.wesnoth_hexmap_factory)

# class Peasant(cocos.sprite.Sprite):
#   def __init__(self):
#       super( Peasant, self).__init__("assets/peasant.png")
#
#   def go_to_cell(self, cell):
#       self.position = cell.center


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

            self.set_focus(
                self.start_focus[0] + self.start_drag[0] - x,
                self.start_focus[1] + self.start_drag[1] - y
            )


class Sandbox(cocos.layer.ColorLayer, pyglet.event.EventDispatcher):
    is_event_handler = True

    def __init__(self, mapFile):
        super(Sandbox, self).__init__(20, 20, 20, 255)

        r = cocos.tiles.load(mapFile)
        level1 = r['level1']

        manager = DraggableScrollingManager()
        manager.add(level1)
        self.manager = manager
        self.add(manager)

        # level1.set_view(0, 0, level1.px_width, level1.px_height)
        self.current_map = level1
        self.clicked = False

    def get_tile_at_virtual_coord(self, x, y):
        pixel_from_screen = self.manager.pixel_from_screen(x, y)
        return self.current_map.get_at_pixel(*pixel_from_screen)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.clicked = self.get_tile_at_virtual_coord(x, y)

    def on_mouse_release(self, x, y, buttons, modifiers):
        left_button = buttons & pyglet.window.mouse.LEFT
        clicked = self.clicked
        if left_button and clicked and (clicked == self.get_tile_at_virtual_coord(x, y)):
            clicked, self.clicked = self.clicked, None
            return self.dispatch_event('on_tile_clicked', clicked)

    def on_resize(self, width, height):
        if width > self.width or height > self.height:
            self.width, self.height = width, height
            self.on_exit()
            self.on_enter()


Sandbox.register_event_type('on_tile_clicked')

if __name__ == '__main__':
    import sys
    sys.path.append('../../src')

    from economy import economy
    map_file = 'map1.xml'

    if map_file == 'map1.xml':
        e = economy.Economy(('wood', 'ore'))

        e.add_city(name='town a', inventory=dict(wood=200, ore=100))
        e.add_city(name='town b', inventory=dict(wood=300, ore=150))
        e.add_city(name='town c', inventory=dict(wood=100, ore=500))

        e.add_route(name='town a self', ini="town a", end="town a", traffic=dict(wood=0.3,ore=0.8))
        e.add_route(name='a-b path', ini="town a", end="town b", traffic=dict(wood=0.3,ore=0.1))
        e.add_route(name='a-c path', ini="town a", end="town c", traffic=dict(wood='rest',ore='rest'))

        e.add_route(name='b-c smuggle', ini="town b", end="town c", traffic=dict(wood=0.1,ore=0.0))
        e.add_route(name='b-a path', ini="town b", end="town a", traffic=dict(wood=0.1,ore=0.9))
        e.add_route(name='town b self', ini="town b", end="town b", traffic=dict(wood="rest",ore="rest"))

        e.add_route(name='town c self', ini="town c", end="town c", traffic=dict(wood="rest",ore="rest"))

        colors = [('ore', (255, 0, 0)), ('wood', (0,0,255))]
    elif map_file == 'map2.xml':
        pass

    cocos.director.director.init(do_not_scale = True, resizable = True)

    sbx = Sandbox(map_file)

    #Widgets
    from cocosExtension.widgets import EconomyInspector, SidePanel
    main_scene = cocos.scene.Scene (sbx)
    try:
        h = EconomyInspector(e, sbx.current_map)
        sp = SidePanel(h)

        h.position = (0, 50)
        for tradeable, color in colors:
            h.tradeable_color(tradeable, color)

        sbx.push_handlers(h)
        sbx.add(h)
        sbx.add(sp)
        def update():
            e.step()
            h.update()
        main_scene.schedule_interval(lambda x: update(), 2)
    except NameError:
        pass



    cocos.director.director.economy = e
    cocos.director.director.run(main_scene)
