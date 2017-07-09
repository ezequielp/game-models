(ns eco.vegetation-test
  (:require [clojure.test :refer :all]
            [eco.vegetation :refer :all]))



(defn- scale [x y]
  (if (or (zero? x) (zero? y))
    1
    (Math/abs x)))

(defn float=
  ([x y] (float= x y 0.00001))
  ([x y epsilon] (<= (Math/abs (- x y))
                     (* (scale x y) epsilon))))

(defn vect-within-error [Va Vb]
  (every? #(apply float= %1) (map vector Va Vb)))

(def tree-type-a {:consumption  [1     1   0.9]
                  :need-growth  [0.75  1   0.8]
                  :need-survive [0.5   0.5 0.7]
                  :max-size 5
                  :max-age  100
                  :fertile-age 10
                  :seeds-per-fruit 5
                  :drop-on-dead [0.5  1   0.5]})

(def cell
      {
        :resources  {:current     [10    8  10]
                     :max         [100 100 100]
                     :production  [  1   0.5   0.5]}
        :tree {:type             tree-type-a
               :resource-storage [0 0 0]
               :size             1
               :is-dead false}
        :seeds [0 0 0]})

(def depleted-cell
  "This cell doesn't have resources but will have enough production to sustain
  a tree"
  (assoc-in cell [:resources :current] [0 0 0.2]))

(def depleted-and-dry-cell
  "This cell doesn't produce one of its resources"
  (assoc-in depleted-cell [:resources :production] [0.1 0.1 1]))

(deftest consumption-growth-step-test
  (testing "A single step updates tree size and resources correctly"
    (let [updated-cell (update-cell cell)]
      (is (not (get-in cell [:tree :is-dead])))
      (is (vect-within-error   (get-in updated-cell [:tree :resource-storage]) [0.25 0 0.1])) ; initial resource_storage + type consumption - need-growth
      (is (=                   (get-in updated-cell [:tree :size])              2))
      (is (vect-within-error   (get-in updated-cell [:resources :current])     [10 7.5 9.6]))))) ; initial resources + production - type consumption

(deftest consumption-just-survive-test
  (testing "If there are just enough resources, tree can still survive"
    (let [updated-cell (update-cell depleted-cell)]
      (is (not (get-in cell [:tree :is-dead])))
      (is (vect-within-error (get-in updated-cell [:tree :resource-storage]) [0.5 0 0]))
      (is (=                 (get-in updated-cell [:tree :size])             1))
      (is (vect-within-error (get-in updated-cell [:resources :current])     [0 0 0])))))

(deftest consumption-not-enough-resources-test
  (testing "If there are not enough resources, the tree will die and drop resources"
    (let [updated-cell (update-cell depleted-and-dry-cell)]
      (is (= nil (get updated-cell :tree)))
      (is (vect-within-error (get-in updated-cell [:resources :current]) [0.5 1 0.8]))))) ; initial resources + production - clamped consumption + resource drop
