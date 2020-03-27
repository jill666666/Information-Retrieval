/*
 * Calaca - Search UI for Elasticsearch
 * https://github.com/romansanchez/Calaca
 * http://romansanchez.me
 * @rooomansanchez
 * 
 * v1.2.0
 * MIT License
 */

/* Service to Elasticsearch */
Calaca.factory('calacaService', ['$q', 'esFactory', '$location', function($q, elasticsearch, $location){

    var client = elasticsearch({ host: CALACA_CONFIGS.url });

    client.ping({
        requestTimeout: 10000
    }, function(error){
        if (error) {
            console.trace('elasticsearch cluster is down!');
            console.trace(error);
        } else {
            console.log('All is well');
        }
    });


    var search = function(query, mode, offset){

        var deferred = $q.defer();

        if (query.length == 0) {
            deferred.resolve({ timeTook: 0, hitsCount: 0, hits: [] });
            return deferred.promise;
        }

        client.search({
                "index": 'merged_index',
                "body": {
                    "size": 5,
                    "query": {
                        "query_string": {
                            "query": query
                        }
                    }
                }
        }).then(function(result) {
                var i = 0, hitsIn, hitsOut = [], source;
                hitsIn = (result.hits || {}).hits || [];
                for(;i < hitsIn.length; i++){
                    source = hitsIn[i]._source;
                    source._id = hitsIn[i]._id;
                    source._index = hitsIn[i]._index;
                    source._type = hitsIn[i]._type;
                    source._score = hitsIn[i]._score;
                    hitsOut.push(source);
                }
                deferred.resolve({ timeTook: result.took, hitsCount: result.hits.total, hits: hitsOut });
        }, deferred.reject);

        return deferred.promise;
    };

    return {
        "search": search
    };

    }]
);
