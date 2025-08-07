from flask import Flask, request
import pymongo

app = Flask(__name__)

# Connect to the database
db_client = pymongo.MongoClient("mongodb://mongo1:27017")
db = db_client['pages']

"""
Searches the database of pages given various search criteria.
"""
@app.get("/search")
def search():
    query = '+'.split(request.args.get('q', default=None))
    num_results = int(request.args.get('n', default=10))

    return str(get_by_relevance(query, num_results))

"""
Sorts a collection in the database by relevance to a given list of search terms
"""
def get_by_relevance(terms: list, num_entries: int) -> list:
    return db.en.aggregate([
        {
            '$set' : {
                'title_score' : {'$size' : {'$filter' : {
                    'input' : "$title",
                    'as' : 'item',
                    'cond' : {'$in' : ['$item', terms]}
                }}},
                'keywords_score' : {'$size' : {'$filter' : {
                    'input' : "$keywords",
                    'as' : 'item',
                    'cond' : {'$in' : ['$item', terms]}
                }}},
                'description_score' : {'$size' : {'$filter' : {
                    'input' : "$description",
                    'as' : 'item',
                    'cond' : {'$in' : ['$item', terms]}
                }}},
                'body_score' : {'$size' : {'$filter' : {
                    'input' : "$body",
                    'as' : 'item',
                    'cond' : {'$in' : ['$item', terms]}
                }}}
            }
        },
        {
            '$set' : {
                'total_score' : {'$sum' : [
                    '$title_score',
                    '$keywords_score',
                    '$description_score',
                    '$body_score',
                ]}
            }
        },
        {'$sort' : {'total_score' : -1}},
        {'$limit' : num_entries},
        {'$unset' : ['title_score', 'keywords_score', 'description_score', 'body_score', 'total_score']},
        {'$project' : {'_id' : 0, 'url' : 1}}
    ]).to_list()