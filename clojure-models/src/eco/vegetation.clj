(ns eco.vegetation
  (:gen-class))

(defn- sub-by-vect [B]
  "Operation that subtracts B from vector"
  (fn [A]
    (map - A B)))

(defn- add-vecs [A B]
  (map + A B))

(defn- add-to-vect [B]
  "Operation that adds B to vector"
  (fn [A]
    (add-vecs A B)))

(defn sub-vect [A B]
  (map - A B))

(defn- clamp-to [V Vclamp]
  "Returns copy of V where each coordinate is clamped to
  coordinates of Vclamp"
  (map min V Vclamp))

(defn- scale-by [k V]
  (cond (= k 1) V
        :else  (map #(* k %) V)))

(defn- sattisfies [V Vtarget]
  (every? #(apply >= %) (map vector V Vtarget)))

(defn- increase [cell & {:keys [field, amount, up-to, multiplier, source]
                         :or {multiplier [(gensym)]
                              source nil
                              up-to nil}}]
  {:pre [(not (nil? amount)) (not (nil? field))]}
  "Update cell by adding the contents of 'amount' to 'field'
   Optional parameters
      :source - Subtract as much resources as possible from source.
                If source is not enough, clamp increase to available amount
      :up-to - Make sure final values of 'field' are not greater than values of 'up-to'"
  (let [multiply-by (get-in cell multiplier 1)
        transfer (scale-by multiply-by (get-in cell amount))
        ;; transfer can be at most what is available at source
        clamped-transfer (if source
                           (clamp-to transfer (get-in cell source))
                          transfer)
        increase-to (add-vecs (get-in cell field) clamped-transfer)
        clamped-final (if up-to
                        (clamp-to increase-to (get-in cell up-to))
                        increase-to)]
      (if source
         (let [transfer-final (sub-vect clamped-final (get-in cell field))]
           (-> cell (update-in field  (add-to-vect transfer-final))
                    (update-in source (sub-by-vect transfer-final))))
         (-> cell (assoc-in field clamped-final)))))

(defn- consume-resource [cell]
  (increase cell :field  [:tree :resource-storage]
                 :amount [:tree :type :consumption]
                 :source [:resources :current]))

(defn- produce-resources [cell]
  (increase cell
      :field [:resources :current]
      :amount [:resources :production]
      :up-to [:resources :max]))

(defn- grow-tree [cell]
  (let [tree (:tree cell)
        {:keys [type resource-storage size]} tree
        need-to-grow    (scale-by size (:need-growth type))
        need-to-survive (scale-by size (:need-survive type))]
    (cond
      (sattisfies resource-storage need-to-grow)    (-> cell
                                                     (update-in [:tree :size] inc)
                                                     (update-in [:tree :resource-storage] (sub-by-vect need-to-grow)))
      (sattisfies resource-storage need-to-survive) (-> cell
                                                     (update-in [:tree :resource-storage] (sub-by-vect need-to-survive)))
      :else (assoc-in cell [:tree :is-dead] true))))

(defn- recycle [cell]
  (let [dead-tree (get-in cell [:tree :is-dead])]
    (if dead-tree
      (-> cell (increase :field [:resources :current]
                         :amount [:tree :type :drop-on-dead]
                         :multiplier [:tree :size]
                         :up-to [:resources :max])
               (assoc :tree nil))
      cell)))


(defn- feed-tree [cell]
  (if (:tree cell)
      (consume-resource cell)
      cell))

(defn update-cell [cell]
  (-> cell produce-resources
           feed-tree
           grow-tree
           recycle))


(comment
 "Sample cell/tree"
 (def tree-type-1 {:consumption  [1     2   1]
                   :need-growth  [0.75  1   0.8]
                   :need-survive [0.5   0.5 0.9]
                   :max-size 5
                   :max-age  100
                   :fertile-age 10
                   :seeds-per-fruit 5
                   :drop-on-dead [0.5  1   0.5]})
 (def cell
       {
         :resources  {:current     [100 100 100]
                      :max         [100 100 100]
                      :production  [  2   2   2]}
         :tree {:type             tree-type-1
                :resource-storage [0 0 0]
                :size             1
                :is-dead false}
         :seeds [0 0 0]}))
