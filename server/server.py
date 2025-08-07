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
    query = request.args.get('q', default=None)
    num_results = request.args.get('n', default=10)

    return get_by_relevance(query, num_results)

"""
Sorts a collection in the database by relevance to a given list of search terms
"""
def get_by_relevance(terms: list, num_entries: int):
    return db.en.aggregate([
        {
            '$set' : {
                'title_score' : {},
                'keywords_score' : {},
                'body_score' : {}
            }
        },
        {
            '$set' : {
                'total_score' : {}
            }
        },
        {'$sort' : {'total_score' : 1}},
        {'$limit' : num_entries},
        {'$unset' : ['title_score', 'keywords_score', 'body_score', 'total_score']}
    ])