import asyncio
import aiohttp

import urllib.robotparser

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

"""
Gets a page at a given url and returns it
"""
@asyncio.coroutine
def get(url: str):
    req = yield from aiohttp.request('GET', url)
    return (yield from req.read_and_close(decode=True))


@asyncio.coroutine
def crawl(url: str, depth: int):
    # Get and parse the page
    page = yield from get(url)
    doc = BeautifulSoup(page.text, 'html.parser')

    # Get robots.txt
    robot = urllib.robotparser.RobotFileParser()
    robot.set_url(url+"robots.txt")
    robot.read()

    # Get links from document
    links = list()
    link_tags = doc.find_all('a')
    for tag in link_tags:
        link = tag['href']
        # Check if robots.txt allows us to visit this page
        if link != None and link != "" and robot.can_fetch('*', link):
            # Handle absolute and relative URLs
            if link[:4] == 'http':
                # print(f"Absolute URL: {link}")
                links.append(link)
            elif link[0] == '/':
                # print(f"Relative URL: {link}")
                links.append(url[:-1] + link) 
    
    # Yield page info
    yield doc.text
    # Recursively crawl links
    for l in links:
        yield crawl(l, depth - 1)
