import tiles
import unittest
import cocos

class TilesTestCase(unittest.TestCase):
	def setUp(self):
		class MockMap(tiles.WesnothHexMap):
			def __init__(self):
				th = tw = self.tw = self.th = 72
				h_edge2 = self.h_edge2 = 18
				s = self.s = (tw/2-h_edge2)/2
				self.m = -th/(4*s)
				self.avg_width = tw/2+h_edge2
				self.th2 = th/2
		m = MockMap()
		
		self.testlevel = m

	def test_tile_at_position(self):
		#Simple cases: center of tiles
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(65, 44))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(36, 36))
		self.assertEqual((1,0), self.testlevel.get_key_at_pixel(90, 72))
		self.assertEqual((0,1), self.testlevel.get_key_at_pixel(36, 108))
		self.assertEqual((1,1), self.testlevel.get_key_at_pixel(90, 144))
		self.assertEqual((2,2), self.testlevel.get_key_at_pixel(144, 180))
		self.assertEqual((2,1), self.testlevel.get_key_at_pixel(144, 108))
		self.assertEqual((2,0), self.testlevel.get_key_at_pixel(144, 35))

		#Edge cases:
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(58, 35))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(1, 36))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(14, 37))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(28, 37))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(14, 37))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(28, 35))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(44, 37))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(44, 35))
		self.assertEqual((0,0), self.testlevel.get_key_at_pixel(58, 37))
		self.assertEqual((2,0), self.testlevel.get_key_at_pixel(124, 10))

		self.assertEqual((1,0), self.testlevel.get_key_at_pixel(90, 72))
		self.assertEqual((1,0), self.testlevel.get_key_at_pixel(90, 73))
		self.assertEqual((1,0), self.testlevel.get_key_at_pixel(74, 80))
		self.assertEqual((10,5), self.testlevel.get_key_at_pixel(608, 400))



