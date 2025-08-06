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
    num_results = query.args.get('n', default=10)

"""
Sorts a collection in the database by relevance to a given list of search terms
"""
def get_by_relevance(terms: list, num_entries: int):
    pass

"""
Scores a page by how relevant it is to a given list of search terms
"""
def relevance_score(terms: list, page: dict) -> float:
    # Modifiers for different scoring criteria are defined here
    TITLE_SCORE = 10
    KEYWORD_SCORE = 10
    DESCRIPTION_SCORE = 5
    BODY_SCORE = 1
    FOUND_SCALING = 1

    score = 0           # The total similarity score for the page
    terms_found = 0     # A count of the number of search terms found in the page

    for term in terms:
        found = False
        # Term appears in page title
        if term in page['title'][0]:
            score += TITLE_SCORE
            if not found:
                terms_found += 1
                found = True
        # Term appears in keywords
        if page['keywords'] != None and term in page['keywords'][0]:
            score += KEYWORD_SCORE
            if not found:
                terms_found += 1
                found = True
        # Appearences of term in description
        if page['description'] != None:
            score += page['description'][0].count(term) * DESCRIPTION_SCORE
            if not found and term in page['description'][0]:
                terms_found += 1
                found = True
        # Appearances of term in body (divided by length of the body)
        if page['body'] != None:
            score += (page['body'][0].count(term) / len(page['body'][0].split(' '))) * BODY_SCORE
            if not found and term in page['body'][0]:
                terms_found += 1
                found = True

    # Multiply score my number of terms found, times a scaling factor
    score = score * terms_found * FOUND_SCALING

    return score