import unittest
import market


class MarketTestCase(unittest.TestCase):
    def setUp(self):
        self.marketA = market.Market((4, 20), 'seed')

    def test_inventory(self):
        marketA = self.marketA
        self.assertEquals(4, len(marketA.inventory()))
        self.assertEquals(20, sum(marketA.inventory().values()))

    def test_inventory_state_deltas_after_buy(self):
        marketA = self.marketA
        boughtFrom = next(i for i in range(4) if marketA.merchant(i).buy(4))
        self.assertTrue(boughtFrom is not None)
        self.assertEquals(16, sum(marketA.inventory().values()))
        self.assertEquals((4, 20), marketA.state())
        self.assertEquals(1, len(marketA.deltas()))
        self.assertEquals(-4, marketA.deltas()[boughtFrom])

    def test_inventory_state_deltas_after_sell(self):
        marketA = self.marketA
        self.assertTrue(marketA.merchant(0).sell(4))
        self.assertEquals(24, sum(marketA.inventory().values()))
        self.assertEquals((4, 20), marketA.state())
        self.assertEquals(1, len(marketA.deltas()))
        self.assertEquals(4, marketA.deltas()[0])

    def test_market_back_after_leave(self):
        next(i for i in range(4) if self.marketA.merchant(i).buy(4))
        old_stocks = [self.marketA.merchant(i).inventory() for i in range(4)]
        deltas = self.marketA.deltas()
        state = self.marketA.state()
        del self.marketA

        marketB = market.Market(state, 'seed', deltas)
        stocks = [marketB.merchant(i).inventory() for i in range(4)]
        self.assertEquals(old_stocks, stocks)

    def test_market_back_after_long_leave(self):
        old_stocks = [self.marketA.merchant(i).inventory() for i in range(4)]
        deltas = self.marketA.deltas()
        state = self.marketA.state()
        del self.marketA

        marketB = market.Market(state, 'new_seed', deltas)
        stocks = [marketB.merchant(i).inventory() for i in range(4)]
        self.assertNotEquals(old_stocks, stocks)
