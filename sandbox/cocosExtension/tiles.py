from cocos import tiles
from math import floor

class WesnothHexCell(tiles.HexCell):
    def __init__(self, i, j, height, properties, tile):
        width = height
        tiles.Cell.__init__(self, i, j, width, height, properties, tile)

class WesnothHexMap(tiles.HexMap):
    def __init__(self, id, th, cells, origin=None, properties=None):
        tiles.HexMap.__init__(self, id, th, cells, origin, properties)
        self.tw = th


    def get_key_at_pixel(self, x, y):
        """returns the grid coordinates for the hex that covers the point (x, y)

        Reference:
            Hexagonal grid math, by Ruslan Shestopalyuk
            http://blog.ruslans.com/2011/02/hexagonal-grid-math.html
        """
        th, tw = self.th, self.tw
        
        x, y = x-tw/2, y-th/2
        lattice_i = x // (3*th/4)
        lattice_j = (y - lattice_i*th/2) // tw
        
        def distance(i, j):
            return (x- 3*i*th/4)**2+(y-j*th-i*th/2)**2

        closest = min( ((lattice_i+di, lattice_j+dj) for di in [0, 1] for dj in [0, 1] if dj*di == 0), key = lambda x: distance(*x))
        
        return  closest[0], closest[1]+closest[0]//2

class WesnothHexMapLayer(WesnothHexMap, tiles.MapLayer):
    def __init__(self, id, th, cells, origin=None, properties=None):
        WesnothHexMap.__init__(self, id, th, cells, origin, properties)
        tiles.MapLayer.__init__(self, properties)

def wesnoth_hexmap_factory(resource, tag):
    height = int(tag.get('tile_height'))
    width = height
    origin = tag.get('origin')
    if origin:
        origin = map(int, tag.get('origin').split(','))
    id = tag.get('id')

    # now load the columns
    cells = []
    for i, column in enumerate(tag.getiterator('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getiterator('cell')):
            tile = cell.get('tile')
            if tile:
                tile = resource.get_resource(tile)
            else:
                tile = None
            properties = tiles._handle_properties(tag)
            c.append(WesnothHexCell(i, j, height, properties, tile))

    properties = tiles._handle_properties(tag)
    m = WesnothHexMapLayer(id, height, cells, origin, properties)
    resource.add_resource(id, m)

    return m