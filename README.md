# Web & File Crawler

This project is a Python-based crawler capable of crawling **file storage**, **dynamic and static websites**, and **databases**. It allows indexing data into Elasticsearch for efficient searching and retrieval.

## Features

- **File Storage Crawler**: Crawls directories and files, indexing them into Elasticsearch.
- **Website Crawling**:
  - **Static Websites**: Crawls traditional HTML pages using Scrapy.
  - **Dynamic Websites**: Uses Selenium to crawl JavaScript-rendered content.
- **Database Crawler**: Extracts and indexes data from databases.
- **Elasticsearch Integration**: Indexes crawled data into Elasticsearch, using URLs as unique keys to avoid duplication.

## Prerequisites

- **Python**: Ensure Python 3.x is installed.
- **Elasticsearch**: Install and run Elasticsearch (version 7.x or above).
- **Chrome WebDriver**: Needed for dynamic website crawling using Selenium.
- **Dependencies**: Install Python packages via pip:

```bash
pip install -r requirements.txt
