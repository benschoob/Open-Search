import asyncio
import string
import aiohttp

from time import time

import urllib.robotparser

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

import pymongo

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Connect to the database
db_client = pymongo.MongoClient("mongodb://mongo1:27017")
db = db_client['pages']

seen = set()


"""
Gets a page at a given url and returns it
"""
async def get(url: str) -> str:
    async with aiohttp.request('GET', url) as response:
        return await response.text()

"""
Crawls a page at a given URL and recursively crawls all pages linked on that page
"""
async def crawl(url: str, depth: int):
    # Get and parse the page
    try:
        page = await get(url)
    except:
        print("ERROR Connection Timeout")
        return []
    
    doc = BeautifulSoup(page, 'html.parser')

    # Check document language (for now, we only want english language pages)
    html = doc.find('html')
    if html.has_attr('lang') and (html['lang'] != 'en' and html['lang'] != 'en-US'):
        return [] # We don't want to crawl this page

    # Get robots.txt
    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(url+"robots.txt")
    try:
        robot.read()
    except:
        print(f"ERROR reading robots.txt for {url}")
        return []

    # Get links from document
    links = []
    link_tags = doc.find_all('a')
    for tag in link_tags:
        if tag.has_attr('href'):
            link = tag['href']
            # Check if robots.txt allows us to visit this page
            if link != None and link != "" and robot.can_fetch('*', link):
                # Handle absolute and relative URLs
                if link[:4] == 'http':
                    # print(f"Absolute URL: {link}")
                    links.append(link)
                # TODO: fix relative links
                #elif link[0] == '/':
                    # print(f"Relative URL: {link}")
                    #links.append(url + link) 
    
    print(f"Crawled {url}")

    # Create new tasks
    tasks = []

    # Database entry task
    obj = parse_page(doc, url)
    print(obj)
    tasks.append(asyncio.create_task(add_to_db(obj, db)))

    # Recursive crawl tasks
    if (depth > 0):
        for l in links:
            if l not in seen:
                seen.add(l)
                tasks.append(asyncio.create_task(crawl(l, depth - 1)))

    # Return the tasks
    return tasks

"""
Parses relevant information from an HTML page and returns it in a dictionary
"""
def parse_page(doc: BeautifulSoup, url: str) -> dict:
    # Store page contents as lists of strings (without punctuation)
    title = ' '.split(doc.find('title').contents[0])

    desc = doc.find('meta', {'name' : 'description'})
    if desc != None:
        desc = ' '.split(desc['content'][0].translate(str.maketrans("", "", string.punctuation)))
    else:
        desc = []

    keywords = doc.find('meta', {'name': 'keywords'})
    if keywords != None:
        keywords = ' '.split(keywords['content'][0].translate(str.maketrans("", "", string.punctuation)))
    else:
        keywords = []

    body = ' '.split(' '.join([s for s in doc.body.strings]).translate(str.maketrans("", "", string.punctuation)))

    return {
        'url'           : url,
        'title'         : title,
        'description'   : desc,
        'keywords'      : keywords,
        'body'          : body,
    }

"""
Sends a dictionary to the MongoDB database as a JSON object
"""
async def add_to_db(obj: dict, db: pymongo.database):
    col = db['en'] # Add to the collection of english-language pages
    col.update_one(
        {'url' : obj['url']},
        {
            '$set' : {
                'url'           : obj['url'],
                'title'         : obj['title'],
                'description'   : obj['description'],
                'keywords'      : obj['keywords'],
                'body'          : obj['body']
            }
        },
        upsert=True # If the document doesn't exist, create it
    )
    return [] # Don't need to return any additional tasks

"""
Parses crawler seeds from seeds.txt file
"""
def parse_seeds(file_path: str) -> list:
    seeds = []
    with open(file_path) as f:
        for line in f:
            if line[0] != '#' and not line.isspace(): # Ignore comments and empty lines
                seeds.append(line)
    return seeds

"""
Flattens a list of lists into a single list
"""
def flatten(lol: list):
    return [e for l in lol for e in l]


async def main():
    # Parse seeds.txt
    seeds = parse_seeds('./seeds.txt')
    if len(seeds) == 0:
        print("ERROR: no seeds provided. You can add seeds by editing 'seeds.txt'.")
        exit(1)

    depth = 0

    # Generate initial tasks
    tasks = []
    for s in seeds:
        seen.add(s)
        task = asyncio.create_task(crawl(s, depth))
        tasks.append(task)

    # Run the tasks in queue until the queue runs out
    start_time = time()
    while len(tasks) > 0:
        results = await asyncio.gather(*tasks)
        tasks = flatten(results)
    end_time = time()

    # Print crawl stats
    print(f"Crawl complete. Time elapsed: {end_time - start_time:.2f}s. Pages seen: {len(seen)}")

# Start the main program loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
