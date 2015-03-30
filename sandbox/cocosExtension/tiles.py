from cocos import tiles
from math import floor

class WesnothHexCell(tiles.HexCell):
    def __init__(self, i, j, height, properties, tile):
        width = height
        tiles.Cell.__init__(self, i, j, width, height, properties, tile)

class WesnothHexMap(tiles.HexMap):
    def get_key_at_pixel(self, x, y):
        """returns the grid coordinates for the hex that covers the point (x, y)

        Reference:
            Hexagonal grid math, by Ruslan Shestopalyuk
            http://blog.ruslans.com/2011/02/hexagonal-grid-math.html
        """
        radius = self.edge_length
        side = (self.tw * 3) // 4
        height = self.th

        ci = int(floor(x / side))
        cx = int(x - side*ci)

        ty = int(y - (ci % 2) * height / 2.0)
        cj = int(floor(1.0 * ty / height))
        cy = ty - height * cj

        if cx <= abs(radius/2.0 - radius*cy/height):
            cj = cj + (ci % 2) - (1 if (cy < height / 2.0) else 0)
            ci = ci - 1
        return ci, cj

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