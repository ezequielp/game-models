import economy
import unittest
from collections import namedtuple

Goods = namedtuple("Goods", ('swords'))


class EconomyTestCase(unittest.TestCase):
    def setUp(self):
        self.economy = economy.Economy(tradeables=Goods._fields)
        add_route = self.economy.add_route
        add_market = self.economy.add_market

        add_market("town a", inventory=Goods(10))
        add_market("town b", inventory=Goods(20))
        add_market("town c", inventory=Goods(30))
        add_market("town d", inventory=Goods(25))

        add_route("route 1", start="town a", end="town b", traffic=Goods(0.8))
        add_route("route 2", start="town a", end="town c", traffic=Goods("rest"))
        add_route("route 3", start="town b", end="town a", traffic=Goods(0.3))
        add_route("route 4", start="town b", end="town c", traffic=Goods(0.6))
        add_route("route 5", start="town b", end="town b", traffic=Goods("rest"))
        add_route("route 6", start="town c", end="town b", traffic=Goods(0.4))
        add_route("route 7", start="town c", end="town d", traffic=Goods("rest"))
        add_route("route 8", start="town d", end="town d", traffic=Goods("rest"))

    def test_contains(self):
        """Economy can be queried for its components in a pythonic way"""
        self.assertTrue("town a" in self.economy)
        # self.assertTrue("route 1" in self.economy)  # Is this useful?

    def test_route(self):
        """"We can query goods trade on each route"""
        economy = self.economy
        self.assertAlmostEqual(0.8, economy.traffic("route 1", "swords"))
        self.assertAlmostEqual(0.2, economy.traffic("route 2", "swords"))
        self.assertAlmostEqual(0.3, economy.traffic("route 3", "swords"))
        self.assertAlmostEqual(0.6, economy.traffic("route 4", "swords"))
        self.assertAlmostEqual(0.1, economy.traffic("route 5", "swords"))

    def test_market(self):
        """We can query goods existences on each market"""
        economy = self.economy
        self.assertEqual(10, economy.stock("town a", "swords"))
        self.assertEqual(20, economy.stock("town b", "swords"))
        self.assertEqual(30, economy.stock("town c", "swords"))
        self.assertEqual(25, economy.stock("town d", "swords"))

    def test_route_default_traffic(self):
        """I'm assuming defining a route without traffic sets it
        to what it takes to add up to 1"""
        route = self.economy.traffic

        self.economy.step()

        self.assertAlmostEqual(0.2, route("route 2", "swords"))
        self.assertAlmostEqual(0.1, route("route 5", "swords"))

    def test_step(self):
        economy = self.economy
        """Test that running one step modifies market existences"""
        economy.step()

        # Existences on each market change
        self.assertEqual(6, economy.stock("town a", "swords"))
        self.assertEqual(22, economy.stock("town b", "swords"))
        self.assertEqual(14, economy.stock("town c", "swords"))
        self.assertEqual(43, economy.stock("town d", "swords"))

        # Routes are not affected
        self.assertAlmostEqual(0.8, economy.traffic("route 1", "swords"))
        self.assertAlmostEqual(0.2, economy.traffic("route 2", "swords"))
        self.assertAlmostEqual(0.3, economy.traffic("route 3", "swords"))
        self.assertAlmostEqual(0.6, economy.traffic("route 4", "swords"))
        self.assertAlmostEqual(0.1, economy.traffic("route 5", "swords"))

    def test_find_routes(self):
        """More complex queries can be performed"""
        return
        route_finder = self.economy.find_routes
        from_town_a = set(
            ("route 1", "town a", "town b"),
            ("route 2", "town a", "town b")
        )
        from_town_b = set(
            ("route 3", "town b", "town a"),
            ("route 4", "town b", "town c"),
            ("route 5", "town b", "town b")
        )
        to_town_a = set(("route 3", "town b", "town a"))
        to_town_b = set(
            ("route 1", "town a", "town b"),
            ("route 5", "town b", "town b"),
            ("route 6", "town c", "town b")
        )
        self.assertEqual(from_town_a, route_finder(source="town a"))
        self.assertEqual(from_town_b, route_finder(source="town b"))

        self.assertEqual(to_town_a, route_finder(destination="town a"))
        self.assertEqual(to_town_b, route_finder(destination="town b"))
