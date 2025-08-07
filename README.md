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