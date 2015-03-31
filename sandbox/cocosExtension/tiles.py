from cocos import tiles
from math import floor

class WesnothHexCell(tiles.HexCell):
    def __init__(self, i, j, height, properties, tile):
        width = height
        tiles.Cell.__init__(self, i, j, width, height, properties, tile)

class WesnothHexMap(tiles.HexMap):
    def __init__(self, id, th, cells, origin=None, properties=None):
        tiles.HexMap.__init__(self, id, th, cells, origin, properties)
        th = tw = self.tw = self.th = th
        h_edge2 = self.h_edge2 = th/4
        s = self.s = (tw/2-h_edge2)/2
        self.m = -th*1.0/(4*s)
        self.avg_width = tw/2+h_edge2
        self.th2 = th/2


    def get_key_at_pixel(self, x, y):
        """returns the grid coordinates for the hex that covers the point (x, y)

        Reference:
            Hexagonal grid math, by Ruslan Shestopalyuk
            http://blog.ruslans.com/2011/02/hexagonal-grid-math.html
        """
        th, tw, h_edge2, th2 = self.th, self.tw, self.h_edge2, self.th2
        avg_width = self.avg_width
        s = self.s
        m = self.m

        x = x-s
        i, x = divmod(x, avg_width)

        if i%2: # Odd rows are half tile up
            y = y-th2 
        
        j, y = divmod(y, th)

        # reference x,y from center of the tile to simplify math
        x = x-h_edge2-s
        y = y-th2

        if y<=0:
            dy = 0
            y = -y
        elif y>0:
            dy = 1

        if x<0:
            x = -x
            dx = -1
        else:
            dx = 1
            dy = -dy

        if x>h_edge2:
            x = x- h_edge2 
            if y > m*x+th2:
                i = i + dx
                j = j + dy
        
        return (i,j)


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