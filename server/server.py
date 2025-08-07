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
    query = request.args.get('q', default=None).lower().split()
    num_results = int(request.args.get('n', default=10))

    return str(get_by_relevance(query, num_results))

"""
Sorts a collection in the database by relevance to a given list of search terms
"""
def get_by_relevance(terms: list, num_entries: int) -> list:
    # Scaling factors for appearance of search terms in different parts of the documents
    TITLE_SCALE = 10
    KEYWORD_SCALE = 5
    DESCRIPTION_SCALE = 5
    BODY_SCALE = 1

    return db.en.aggregate([
        {
            '$set' : {
                'title_score' : {'$size' : {'$filter' : {
                    'input' : "$title",
                    'as' : 'item',
                    'cond' : {'$in' : ['$$item', terms]}
                }}},
                'keywords_score' : {'$size' : {'$filter' : {
                    'input' : "$keywords",
                    'as' : 'item',
                    'cond' : {'$in' : ['$$item', terms]}
                }}},
                'description_score' : {'$size' : {'$filter' : {
                    'input' : "$description",
                    'as' : 'item',
                    'cond' : {'$in' : ['$$item', terms]}
                }}},
                'body_score' : {'$size' : {'$filter' : {
                    'input' : "$body",
                    'as' : 'item',
                    'cond' : {'$in' : ['$$item', terms]}
                }}}
            }
        },
        {
            '$set' : {
                'total_score' : {'$sum' : [
                    {'$multiply' : ['$title_score', TITLE_SCALE]},
                    {'$multiply' : ['$keywords_score', KEYWORD_SCALE]},
                    {'$multiply' : ['$description_score', DESCRIPTION_SCALE]},
                    {'$multiply' : ['$body_score', BODY_SCALE]},
                ]}
            }
        },
        {'$sort' : {'total_score' : pymongo.DESCENDING}},
        {'$limit' : num_entries},
        #{'$unset' : ['title_score', 'keywords_score', 'description_score', 'body_score', 'total_score']},
        {'$project' : {'_id' : 0, 'url' : 1, 'title' : 1, 'total_score' : 1}}
    ]).to_list()