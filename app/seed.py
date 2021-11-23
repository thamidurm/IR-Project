from elasticsearch import Elasticsearch, helpers
import json

INDEX = 'player-index'

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

with open('../data/data.json', encoding="utf8") as file:
    data = json.loads(file.read())
    helpers.bulk(es, data, index=INDEX)