(defproject trade-routes "0.1.0-SNAPSHOT"
  :description "Double auction models"
  :url "https://github.com/ezequielp/game-models/wiki/Trade-Route-formation-model"
  :license {:name "MIT License"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.8.0"],
                 [org.clojure/data.generators "0.1.2"]]
  :main ^:skip-aot trade-routes.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
