import economy
import unittest
from collections import namedtuple

Goods = namedtuple("Goods", ('swords'))

base_blueprint = economy.EconomyBlueprintFactory() \
    .trades(Goods._fields) \
    .hasMarket("town a", inventory=Goods(10)) \
    .hasMarket("town b", inventory=Goods(20)) \
    .hasMarket("town c", inventory=Goods(30)) \
    .hasMarket("town d", inventory=Goods(25)) \
    .hasRoute("route 1", start="town a", end="town b", traffic=Goods(0.8)) \
    .hasRoute("route 2", start="town a", end="town c", traffic=Goods("rest")) \
    .hasRoute("route 3", start="town b", end="town a", traffic=Goods(0.3)) \
    .hasRoute("route 4", start="town b", end="town c", traffic=Goods(0.6)) \
    .hasRoute("route 5", start="town b", end="town b", traffic=Goods("rest")) \
    .hasRoute("route 6", start="town c", end="town b", traffic=Goods(0.4)) \
    .hasRoute("route 7", start="town c", end="town d", traffic=Goods("rest")) \
    .hasRoute("route 8", start="town d", end="town d", traffic=Goods("rest"))


class EconomyBlueprintFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.bp = base_blueprint

    def test_simpleblueprint(self):
        bp = self.bp.blueprint()
        routes = dict((r.name, r.traffic) for r in bp.routes)
        self.assertAlmostEqual(0.8, routes.get("route 1").swords)
        self.assertAlmostEqual(0.2, routes.get("route 2").swords)
        self.assertAlmostEqual(0.3, routes.get("route 3").swords)
        self.assertAlmostEqual(0.6, routes.get("route 4").swords)
        self.assertAlmostEqual(0.1, routes.get("route 5").swords)
        self.assertAlmostEqual(0.4, routes.get("route 6").swords)
        self.assertAlmostEqual(0.6, routes.get("route 7").swords)
        self.assertAlmostEqual(1, routes.get("route 8").swords)

    def test_validations(self):
        """Tests blueprint construction validations"""
        bp = self.bp
        # Can't add duplicate routes
        with self.assertRaises(NameError):
            bp.hasRoute(
                "route 1", start="town c", end="town d",
                traffic=Goods(0.8)
            ).blueprint()

        # Can't add duplicate market
        with self.assertRaises(NameError):
            bp.hasMarket("town c", inventory=Goods(30)).blueprint()

        # Can only add defined tradeables to markets...
        ExtraneousGoods = namedtuple("Extraneous", ["swords", "wood"])
        with self.assertRaises(KeyError):
            bp.hasMarket("town e", inventory=ExtraneousGoods(10, 20)).blueprint()

        # ...or to routes
        with self.assertRaises(KeyError):
            bp.hasRoute(
                "route weird", start="town a", end="town d",
                traffic=ExtraneousGoods(10, 20)
            ).blueprint()

        # Can't add routes from non existing markets
        with self.assertRaises(NameError):
            bp.hasRoute(
                "route imaginary",
                start="neverland", end="town a",
                traffic=Goods(10)
            ).blueprint()

        with self.assertRaises(NameError):
            bp.hasRoute(
                "route imaginary",
                start="town a", end="neverland",
                traffic=Goods(10)
            ).blueprint()


class EconomyTestCase(unittest.TestCase):
    def setUp(self):
        self.economy = base_blueprint.build()

    def test_contains(self):
        """Economy can be queried for its components in a pythonic way"""
        self.assertTrue("town a" in self.economy)
        # self.assertTrue("route 1" in self.economy)  # Is this useful?

    def test_market(self):
        """We can query goods existences on each market"""
        economy = self.economy
        self.assertEqual(10, economy.stock("town a", "swords"))
        self.assertEqual(20, economy.stock("town b", "swords"))
        self.assertEqual(30, economy.stock("town c", "swords"))
        self.assertEqual(25, economy.stock("town d", "swords"))

    def test_step(self):
        """Test that running one step modifies market existences"""
        economy = self.economy
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

# TODO: decide best way to run complex queries (database?)
#     def test_find_routes(self):
#         """More complex queries can be performed"""
#         return
#         route_finder = self.economy.find_routes
#         from_town_a = set(
#             ("route 1", "town a", "town b"),
#             ("route 2", "town a", "town b")
#         )
#         from_town_b = set(
#             ("route 3", "town b", "town a"),
#             ("route 4", "town b", "town c"),
#             ("route 5", "town b", "town b")
#         )
#         to_town_a = set(("route 3", "town b", "town a"))
#         to_town_b = set(
#             ("route 1", "town a", "town b"),
#             ("route 5", "town b", "town b"),
#             ("route 6", "town c", "town b")
#         )
#         self.assertEqual(from_town_a, route_finder(source="town a"))
#         self.assertEqual(from_town_b, route_finder(source="town b"))

#         self.assertEqual(to_town_a, route_finder(destination="town a"))
#         self.assertEqual(to_town_b, route_finder(destination="town b"))
