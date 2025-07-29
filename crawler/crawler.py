from concurrent.futures import *
from queue import Queue
from time import time

import urllib.robotparser
import warnings

import requests # type: ignore
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning # type: ignore

def crawl(url: str, depth: int, seen: set, tasks: Queue):
    # Get page contents
    r = requests.get(url)
    doc = BeautifulSoup(r.text, "html.parser")

    # Get robots.txt
    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(url+"robots.txt")
    robot.read()

    # TODO: send page data to the database

    # extract links
    links = list()
    link_tags = doc.find_all('a')
    for tag in link_tags:
        link = tag.get('href')
        if link != None and link != "" and robot.can_fetch('*', link):
            if link[:4] == 'http':
                # print(f"Absolute URL: {link}")
                links.append(link)
            elif link[0] == '/':
                # print(f"Relative URL: {link}")
                links.append(url[:-1] + link)   

    # Create new tasks and add them to the queue
    if depth > 0:
        for link in links:
            if not link in seen: # Only look at links we haven't already seen
                seen.add(link)
                tasks.put((link, depth - 1))


def parse_seeds(file_path: str) -> list:
    seeds = []
    with open(file_path) as f:
        for line in f:
            if line[0] != '#' and not line.isspace(): # Ignore comments and empty lines
                seeds.append(line)
    return seeds

# === Main Program ===

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Parse seeds.txt
seeds = parse_seeds('./seeds.txt')
if len(seeds) == 0:
    print("ERROR: no seeds provided. You can add seeds by editing 'seeds.txt'.")
    exit(1)

depth = 2

# Task queue: contains links we need to traverse
tasks = Queue()
for seed in seeds:
    tasks.put((seed, depth))

# Futures queue: hold futures returned by running threads. Used to
# wait for threads to finish
futures = Queue()

# Seen table: tracks what pages we've been to to avoid revisiting pages
seen = set()
for seed in seeds:
    seen.add(seed)

# Crawl stats
pages_crawled = 0

print("Beginning the crawl. . .")
start_time = time()
with ThreadPoolExecutor(max_workers=1000) as e:
    while tasks.qsize() > 0 or futures.qsize() > 0:
        if tasks.qsize() > 0:
            t = tasks.get()
            futures.put(e.submit(crawl, t[0], t[1], seen, tasks)) # Start the task

        # Check if threads have finished
        for _ in range(0, futures.qsize()):
            f = futures.get(timeout=10)
            if not f.done():
                futures.put(f) # Task is not done, put it back on the queue
            else:
                pages_crawled += 1
        print(f"\33[2k\rPages crawled: {pages_crawled}. Pages seen: {len(seen)}. Tasks in queue: {tasks.qsize()}. Futures in queue: {futures.qsize()}.", end="")

end_time = time()

print(f"\nCrawl complete. Pages crawled: {pages_crawled}. Time elapsed: {end_time - start_time:.2f}s")