(ns trade-routes.double-auction
  (:gen-class))


(defn- as-trade-result
  [ask bid]
  (let [bid-price (:price bid)
        ask-price (:price ask)]
    {:traded (<= ask-price bid-price) :bid bid :ask ask}))


(defn- average
  [a b]
  (* 0.5 (+ a b)))


(defn resolve-auction
  "Returns a list of trades and unresolved seller asks orders and buyer bids orders.
  The highest asks are matched with the lowest bids until all bids are greater than all asks.
  [{:price ai} / ai is an ask i=1...K]
  [{:price bi} / bi is a bid i=1...L] =>
  [{:price axi} / axi was a succesful ask i=1..M]
  [{:price byi} / byi was a succesful bid i=1..M]
  breakeven-price
  [{price ayi} / ayi was not a succesful ask i= 1...K-M]
  [{price byi} / byi was not a succesful bid i= 1...L-M]

  TODO: Possible optimization as best-bids can be ordered lazily until all asks are matched."
  [asks bids]
  (let [best-asks (sort-by :price asks)
        best-bids (reverse (sort-by :price bids))
        successful-trades (->> (map as-trade-result best-asks best-bids)
                            (take-while :traded))
        successful-asks  (map :ask successful-trades)
        successful-bids (map :bid successful-trades)
        successful-trades-count (count successful-asks)
        breakeven-price (if (> successful-trades-count 0)
                          (average
                            (->> successful-bids last :price)
                            (->> successful-asks last :price))
                          nil)]
    [successful-asks
     successful-bids
     breakeven-price
     (drop successful-trades-count best-asks)
     (drop successful-trades-count best-bids)]))
