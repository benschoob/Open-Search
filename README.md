# Open-Search

A customizable, open-source search engine built with Docker, Python and MongoDB.

## Dependencies

### Docker

This project is built and run entirely through docker and docker-compose. If you aren't familiar with docker, you can follow the setup guide here: (https://docs.docker.com/desktop/)

## Configuration

Before starting the search engine, you'll need to set up the web crawler that will populate the database. There are two files in `crawler/config` that need to be edited: `seeds.txt` and `crawler.cfg`.

### `seeds.txt`

`seeds.txt` contains the "seeds" for the web crawler. These are URLs of webpages where the crawler will start its crawl. It adds these pages to the database and then recursively crawls to each page linked on that page. The crawler needs at least one URL in `seeds.txt` in order to crawl. Each seed should be on its own line. Comments can be added by starting a line with "#".

### `crawler.cfg`

`crawler.cfg` contains other configuration options for the crawler:
- `crawl_depth` : The recursive depth of the crawl. Note that the duration of the crawl scales exponentially with the depth.
- `time_between_crawls` : The time in seconds that the crawler will wait after a crawl is finished before starting a new crawl. 

## Starting the Engine

The search engine uses three containers which can be build automatically using docker-compose:
```docker
docker-compose build
docker-compose up -d
```
This creates the following containers:
- `crawler1` : Runs the web crawler, populates the database with webpage data.
- `mongo1` : Runs the MongoDB database that handles all of the data collected by the crawler.
- `server1` : Runs a Flask server that lets users search the pages in the database with keywords.

## Querying the Server

The Flask server allows users to search the database with a simple HTTP GET request.
```
[host]/search?q=<search_terms>&n=<num_results>
```
Where `<search_terms>` is a series of search terms separated by '+' and `<num_results>` is an integer. If a number of results is not provided, the server will return 10 results by default.

`[host]` is wherever the server is currently hosted. By default it is hosted on port 5000.

```
eg. localhost:5000/search?q=wikipedia+the+free+encyclopedia&n=100
```

## Using the Frontend

The frontend is currently in development. Please check back later.
