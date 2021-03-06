class Blacksmith:
    def __init__(self, name, swords):
        self.swords = swords
        self.name = name

    def buy(self, quantity):
        if (quantity<=self.swords):
            self.swords -= quantity
            return True
        else:
            return False

    def sell(self, quantity):
        self.swords += quantity
        return True

    def inventory(self):
        return self.swords


import random

def marinbin (nmar, nbin, some=None):
    ## Returns the position of nmar in nbin, allowing the marbles to be in the same bin.
    import itertools
    from time import time

    if nmar == 0:
        return [0]*nbin

    numsymbols = nbin+nmar-1;
    stars = []
    idx = []
    if not some:
        ## This is standard stars and bars.
        for subset in itertools.combinations(range(numsymbols), nmar):
            stars.append(subset);
        ## Star labels minus their consecutive position becomes their index
        ## position!
        for comb in stars:
            r = []
            for i in range(nmar):
                r.append(comb[i]-i)
            idx.append(r)

        nr   = len(idx)
        arng = range(nr)

        c  = [[0]*nbin for i in range(len(arng))]
        for i,a in enumerate(arng):
            for b in range (nmar):
                c[i][idx[a][b]] += 1;

    else:
        for i in range(some):
            stars.append(random_combination(range(numsymbols), nmar))

        ind = random_permutation(range(len(stars)), some)
        for j in range(some):
            r = []
            comb = stars[ind[j]]
            for i in range(nmar):
                r.append(comb[i]-i)
            idx.append(r)
        nr   = len(idx)
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

def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)

def distribute(quantity, total_stock, seed):
    random.seed(seed)
    quantities = marinbin (total_stock, quantity, 1)

    return quantities

class Market:
    def __init__(self, state, seed, deltas = {}):
        (quantity, total_stock) = state
        names = ("Smithy "+chr(ord('A')+i) for i in range(quantity))
        self.generated_stocks = distribute(quantity, total_stock, seed)
        corrected_stocks = list(self.generated_stocks)
        for i, delta in deltas.items():
            corrected_stocks[i] += delta

        self.merchants = [Blacksmith(n, s) for n, s in zip(names, corrected_stocks)]

    def state(self):
        m = (len(self.merchants), sum(self.generated_stocks))
        return m

    def deltas(self):
        deltas = dict((i, merchant.inventory()-stock) for i, (stock, merchant) in enumerate(zip(self.generated_stocks, self.merchants)) if stock != merchant.inventory())
        return deltas

    def inventory(self):
        return dict([(bl.name, bl.inventory()) for bl in self.merchants])


    def merchant(self, i):
        return self.merchants[i]
