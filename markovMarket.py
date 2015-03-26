class Blacksmith:
    def __init__(self, name, swords):
        self.swords = swords
        self.name = name
        
    def buy(self, quantity):
        if (quantity<=self.swords):
            self.swords -= quantity
            self.say("Sold you {} swords".format(quantity))
        else:
            self.say("Can't sell you {} swords. Only have {}".format(quantity, self.swords))
            
            
    def sell(self, quantity):
        self.swords += quantity
        self.say("Bought {} swords from you.".format(quantity))
        
    def inventory(self, quiet = False):
        if not quiet:
            self.say("I have {} swords to sell".format(self.swords));
        return self.swords
        

    def say(self, what):
        print("{}: {}".format(self.name, what))

import random

def marinbin (nmar, nbin, some=None):
    ## Returns the position of nmar in nbin, allowing the marbles to be in the same bin.
    import itertools

    ## This is standard stars and bars.
    numsymbols = nbin+nmar-1;
    stars = []
    for subset in itertools.combinations(range(numsymbols), nmar):
        stars.append(subset);

    ## Star labels minus their consecutive position becomes their index
    ## position!
    idx = []
    for comb in stars:
        r = []
        for i in range(nmar):
            r.append(comb[i]-i)
        idx.append(r)

    nr = len(idx)
    if not some:
        arng = range(nr)

    else:
        arng = random_permutation(range(nr), some)

    c  = [[0]*nbin for i in range(len(arng))]
    for i,a in enumerate(arng):
        for b in range (nmar):
            c[i][idx[a][b]] += 1;

    if some == 1:
        c = c[0]

    return c

def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

def distribute(quantity, total_stock, seed):
    
    random.seed(seed)
    quantities = marinbin (total_stock, quantity, 1)
    
    '''
    quantities = sorted([random.randint(0, total_stock) for i in range(quantity-1)], reverse = True)
    cumulative = [sum(quantities[:i+1]) for i in range(len(quantities))]
    import pdb
    pdb.set_trace()
    if cumulative[-1]>total_stock:
        imax = next(i for i, q in enumerate(cumulative) if q>total_stock)
        cumulative[imax:] = [0]**(10-imax)
    else:
        quantities.append(total_stock-cumulative[-1])
    '''
    return quantities
    
    
class Market:
    def __init__(self, state, seed, deltas = {}):
        (quantity, total_stock, total_delta) = state
        names = ("Smithy "+chr(ord('A')+i) for i in range(quantity))
        self.generated_stocks = distribute(quantity, total_stock-total_delta, seed)
        corrected_stocks = list(self.generated_stocks)
        for i, delta in deltas.items():
            corrected_stocks[i] += delta
        
        self.merchants = [Blacksmith(n, s) for n, s in zip(names, corrected_stocks)]
        
    def state(self):
        deltas = dict((i, merchant.inventory(True)-stock) for i, (stock, merchant) in enumerate(zip(self.generated_stocks, self.merchants)) if stock != merchant.inventory(True))
        m = (len(self.merchants), sum(m.inventory(True) for m in self.merchants), sum(deltas.values()))
        return m, deltas
        
    def inventory(self):
        print("Available merchants: ")
        for bl in self.merchants:
            bl.inventory()
            
    def merchant(self, i):
        return self.merchants[i]
        
        
state = (4, 20, 0)
town_a_market = Market(state, 'seed')

town_a_market.inventory()
town_a_market.merchant(0).buy(1)
town_a_market.inventory()
print("Leaving market")
final_state, deltas = town_a_market.state()

print("Market state",final_state, deltas)
print("Back to market")
town_a_market = Market(final_state, 'seed', deltas)
town_a_market.inventory()
town_a_market.merchant(0).buy(2)
town_a_market.merchant(3).sell(3)
town_a_market.inventory()

print("Leaving market")
final_state, deltas = town_a_market.state()
print("Market state",final_state, deltas)

print("Back to market")
town_a_market = Market(final_state, 'seed', deltas)
town_a_market.inventory()

print("Leaving market for a long while")
final_state, deltas = town_a_market.state()
print("Market state",final_state, deltas)

print("Back to market")
town_a_market = Market(final_state, 'seed1')
town_a_market.inventory()

