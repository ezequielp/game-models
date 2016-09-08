(ns trade-routes.double-auction-test
  (:require [clojure.test :refer :all]
            [trade-routes.double-auction :refer :all]))

(deftest offer-meets-demand-test
  (testing "Trades are correct when there is an intersection between supply and demand"
   (let [bids [{:price 3.5 :name "B1"} {:price 2 :name "B2"} {:price 1 :name "B3"} {:price 0.5 :name "B4"}]
         asks [{:price 2 :name "A1"}   {:price 1 :name "A2"} {:price 0.5 :name "A3"}] 
        [successful-asks succesful-bids breakeven-price unmet-asks unmet-bids] (resolve-auction asks bids)]
    (is (= breakeven-price 1.5))
    (is (= successful-asks  [{:price 0.5 :name "A3"} {:price 1 :name "A2"}]))
    (is (= succesful-bids [{:price 3.5 :name "B1"} {:price 2 :name "B2"}]))
    (is (= unmet-asks [{:price 2 :name "A1"}]))
    (is (= unmet-bids [{:price 1 :name "B3"} {:price 0.5 :name "B4"}])))))

(deftest offer-doesnt-meet-demand-test
  (testing "If the best buyer wants to buy lower than the cheapest seller, no trade will happen."
    (let [bids [{:price 3.5 :name "B1"} {:price 2 :name "B2"} {:price 1 :name "B3"}]
          asks [{:price 4   :name "A1"} {:price 5 :name "A2"} {:price 6 :name "A3"}]
          [successful-asks succesful-bids breakeven-price unmet-asks unmet-bids] (resolve-auction asks bids)]
      (is (= breakeven-price nil))
      (is (= successful-asks []))
      (is (= succesful-bids []))
      (is (= unmet-asks asks))
      (is (= unmet-bids bids)))))

