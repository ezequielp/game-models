import economy
import unittest

ret = object()
ret.__dict__ = {'swords': 1}

return ret


class EconomyTestCase(unittest.TestCase):
	def setUp(self):		

		self.economy = economy.Economy(tradeables = ('swords',))
		
		self.economy.add_market("town a", swords = 10) 
		self.economy.add_market("town b", swords = 20)
		self.economy.add_market("town c", swords = 30)
		self.economy.add_market("town d", swords = 25)

		self.economy.add_route("route 1", from = "town a", to = "town b", traffic = (0.8,))
		self.economy.add_route("route 2", from = "town a", to = "town c", traffic = "rest")

		self.economy.add_route("route 3", from = "town b", to = "town a", traffic = (0.3,))
		self.economy.add_route("route 4", from = "town b", to = "town c", traffic = (0.6,))
		self.economy.add_route("route 5", from = "town b", to = "town b", traffic = "rest")

		self.economy.add_route("route 6", from = "town c", to = "town b", traffic = (0.4,))
		self.economy.add_route("route 7", from = "town c", to = "town d", traffic = "rest")


	def test_contains(self):
		self.assertTrue("town a" in self.economy)
		self.assertTrue("route 1" in self.economy) #Is this useful?

	def test_route(self):
		self.assertEquals(0.7, self.economy.route("route 1", "swords"))
		self.assertEquals(0.3, self.economy.route("route 2", "swords"))
		self.assertEquals(0.3, self.economy.route("route 3", "swords"))
		self.assertEquals(0.1, self.economy.route("route 4", "swords"))
		self.assertEquals(0.6, self.economy.route("route 5", "swords"))

	def test_market(self):
		self.assertEquals(10, self.economy.market("town a", "swords"))
		self.assertEquals(20, self.economy.market("town b", "swords"))
		self.assertEquals(30, self.economy.market("town c", "swords"))
		self.assertEquals(25, self.economy.market("town d", "swords"))

	def test_route_default_traffic(self): #I'm assuming defining a route without traffic sets it to what it takes to add up to 1
		self.economy.step()
		self.assertEquals(0.3, self.economy.route("route 2", "swords"))
		self.assertEquals(0.6, self.economy.route("route 5", "swords"))

	def test_step(self):
		self.economy.step()

		# Existences on each market change
		self.assertEquals(xx, self.economy.market("town a", "swords"))
		self.assertEquals(xx, self.economy.market("town b", "swords"))
		self.assertEquals(xx, self.economy.market("town c", "swords"))
		self.assertEquals(xx, self.economy.market("town d", "swords"))

		# Routes are not affected
		self.assertEquals(0.7, self.economy.route("route 1", "swords"))
		self.assertEquals(0.3, self.economy.route("route 2", "swords"))
		self.assertEquals(0.3, self.economy.route("route 3", "swords"))
		self.assertEquals(0.1, self.economy.route("route 4", "swords"))
		self.assertEquals(0.6, self.economy.route("route 5", "swords"))
