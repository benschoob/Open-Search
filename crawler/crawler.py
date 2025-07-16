from concurrent.futures import *
from queue import Queue
from time import time

import urllib.robotparser

import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

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

# === Main Program ===
seeds = [
    "https://en.wikipedia.org/"
]
depth = 1

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
with ThreadPoolExecutor(max_workers=10) as e:
    while tasks.qsize() > 0 or futures.qsize() > 0:
        if tasks.qsize() > 0:
            t = tasks.get()
            futures.put(e.submit(crawl, t[0], t[1], seen, tasks))
            pages_crawled += 1
        else:
            # Wait for running threads to finish and submit new jobs
            try:
                futures.get().result()
            except:
                print("ERROR handling future.")
end_time = time()

print(f"Crawl complete. Pages crawled: {pages_crawled}. Time elapsed: {end_time - start_time:.2f}s")