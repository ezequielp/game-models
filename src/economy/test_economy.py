import economy
import unittest
from numpy import round

class EconomyTestCase(unittest.TestCase):
	def setUp(self):

		self.economy = economy.Economy(tradeables = ('swords',))

		self.economy.add_market("town a", swords = 10)
		self.economy.add_market("town b", swords = 20)
		self.economy.add_market("town c", swords = 30)
		self.economy.add_market("town d", swords = 25)

		self.economy.add_route("route 1", source = "town a", destination = "town b", traffic = (0.8,))
		self.economy.add_route("route 2", source = "town a", destination = "town c", traffic = ("rest",))

		self.economy.add_route("route 3", source = "town b", destination = "town a", traffic = (0.3,))
		self.economy.add_route("route 4", source = "town b", destination = "town c", traffic = (0.6,))
		self.economy.add_route("route 5", source = "town b", destination = "town b", traffic = ("rest",))

		self.economy.add_route("route 6", source = "town c", destination = "town b", traffic = (0.4,))
		self.economy.add_route("route 7", source = "town c", destination = "town d", traffic = ("rest",))

		self.economy.add_route("route 8", source = "town d", destination = "town d", traffic = ("rest",))

	def test_contains(self):
		self.assertTrue("town a" in self.economy)
		self.assertTrue("route 1" in self.economy) #Is this useful?

	def test_route(self):
		self.assertEqual(0.8, round(1e8*self.economy.route("route 1", "swords"))/1e8)
		self.assertEqual(0.2, round(1e8*self.economy.route("route 2", "swords"))/1e8)
		self.assertEqual(0.3, round(1e8*self.economy.route("route 3", "swords"))/1e8)
		self.assertEqual(0.6, round(1e8*self.economy.route("route 4", "swords"))/1e8)
		self.assertEqual(0.1, round(1e8*self.economy.route("route 5", "swords"))/1e8)

	def test_market(self):
		self.assertEqual(10, self.economy.market("town a", "swords"))
		self.assertEqual(20, self.economy.market("town b", "swords"))
		self.assertEqual(30, self.economy.market("town c", "swords"))
		self.assertEqual(25, self.economy.market("town d", "swords"))

	def test_route_default_traffic(self): #I'm assuming defining a route without traffic sets it to what it takes to add up to 1
		self.economy.step()
		self.assertEqual(0.2, round(1e8*self.economy.route("route 2", "swords"))/1e8)
		self.assertEqual(0.1, round(1e8*self.economy.route("route 5", "swords"))/1e8)

	def test_step(self):
		self.economy.step()

		# Existences on each market change
		self.assertEqual(6, round(1e8*self.economy.market("town a", "swords"))/1e8)
		self.assertEqual(22, round(1e8*self.economy.market("town b", "swords"))/1e8)
		self.assertEqual(14, round(1e8*self.economy.market("town c", "swords"))/1e8)
		self.assertEqual(43, round(1e8*self.economy.market("town d", "swords"))/1e8)

		# Routes are not affected
		self.assertEqual(0.8, round(1e8*self.economy.route("route 1", "swords"))/1e8)
		self.assertEqual(0.2, round(1e8*self.economy.route("route 2", "swords"))/1e8)
		self.assertEqual(0.3, round(1e8*self.economy.route("route 3", "swords"))/1e8)
		self.assertEqual(0.6, round(1e8*self.economy.route("route 4", "swords"))/1e8)
		self.assertEqual(0.1, round(1e8*self.economy.route("route 5", "swords"))/1e8)

	def test_find_routes(self):
		self.assertEqual(set(("route 1", "town a", "town b"), ("route 2", "town a", "town b")), self.economy.find_routes(source = "town a"))
		self.assertEqual(set(("route 3", "town b", "town a"), ("route 4", "town b", "town c"), ("route 5", "town b", "town b")), self.economy.find_routes(source = "town b"))

		self.assertEqual(set(("route 3", "town b", "town a")), self.economy.find_routes(destination = "town a"))
		self.assertEqual(set(("route 1", "town a", "town b"), ("route 5", "town b", "town b"), ("route 6", "town c", "town b")), self.economy.find_routes(destination = "town b"))
		

