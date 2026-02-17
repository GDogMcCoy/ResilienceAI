# ResilienceAI Web Scraping Architecture

## Executive Summary

This document provides a comprehensive web scraping framework for ResilienceAI's data source expansion initiative. The architecture combines Scrapy, BeautifulSoup, and headless browser automation to enable robust, ethical, and scalable data collection from external sources.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Scrapy Framework Implementation](#scrapy-framework-implementation)
3. [BeautifulSoup Parsing Layer](#beautifulsoup-parsing-layer)
4. [Headless Browser Automation](#headless-browser-automation)
5. [Data Extraction Pipelines](#data-extraction-pipelines)
6. [Rate Limiting & Politeness](#rate-limiting--politeness)
7. [Proxy Rotation System](#proxy-rotation-system)
8. [CAPTCHA Handling](#captcha-handling)
9. [Data Validation Framework](#data-validation-framework)
10. [Scheduler Integration](#scheduler-integration)
11. [Legal Compliance](#legal-compliance)
12. [Monitoring & Observability](#monitoring--observability)
13. [Testing Strategy](#testing-strategy)
14. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI Web Scraping System                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scrapy     │  │ BeautifulSoup│  │   Playwright │  │   Selenium   │     │
│  │   Spiders    │  │   Parser     │  │   Browser    │  │   Browser    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│         └─────────────────┴────────┬────────┴─────────────────┘              │
│                                    │                                         │
│                         ┌──────────▼──────────┐                              │
│                         │  Extraction Engine  │                              │
│                         └──────────┬──────────┘                              │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐              │
│         │                          │                          │              │
│  ┌──────▼──────┐          ┌────────▼────────┐        ┌────────▼────────┐     │
│  │   Proxy     │          │  Rate Limiter   │        │   CAPTCHA       │     │
│  │   Manager   │          │                 │        │   Handler       │     │
│  └──────┬──────┘          └────────┬────────┘        └────────┬────────┘     │
│         │                          │                          │              │
│         └──────────────────────────┼──────────────────────────┘              │
│                                    │                                         │
│                         ┌──────────▼──────────┐                              │
│                         │  Data Pipeline      │                              │
│                         └──────────┬──────────┘                              │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐              │
│         │                          │                          │              │
│  ┌──────▼──────┐          ┌────────▼────────┐        ┌────────▼────────┐     │
│  │ Validation  │          │    Storage      │        │   Scheduler     │     │
│  │   Engine    │          │   (MongoDB/     │        │   (APScheduler) │     │
│  │             │          │   PostgreSQL)   │        │                 │     │
│  └─────────────┘          └─────────────────┘        └─────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Spider Engine | Crawl and extract data | Scrapy |
| Parser Layer | HTML/XML parsing | BeautifulSoup4, lxml |
| Browser Automation | JavaScript-heavy sites | Playwright, Selenium |
| Pipeline | Data processing | Custom Python pipelines |
| Rate Limiter | Respectful crawling | Custom middleware |
| Proxy Manager | IP rotation | Proxy provider APIs |
| CAPTCHA Handler | Challenge solving | 2captcha, Anti-Captcha |
| Scheduler | Job orchestration | APScheduler, Celery |
| Validator | Data quality | Pydantic, Cerberus |
| Storage | Data persistence | MongoDB, PostgreSQL |

---

## Scrapy Framework Implementation

### Project Structure

```
resilience_scraper/
├── scrapy.cfg
├── requirements.txt
├── setup.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── proxies.py
│   └── user_agents.py
├── spiders/
│   ├── __init__.py
│   ├── base_spider.py
│   ├── news_spider.py
│   ├── government_spider.py
│   ├── social_media_spider.py
│   └── academic_spider.py
├── middlewares/
│   ├── __init__.py
│   ├── proxy_middleware.py
│   ├── retry_middleware.py
│   ├── rate_limit_middleware.py
│   └── captcha_middleware.py
├── pipelines/
│   ├── __init__.py
│   ├── validation_pipeline.py
│   ├── storage_pipeline.py
│   └── notification_pipeline.py
├── items/
│   ├── __init__.py
│   ├── news_item.py
│   ├── document_item.py
│   └── social_item.py
├── exporters/
│   ├── __init__.py
│   ├── json_exporter.py
│   └── csv_exporter.py
└── utils/
    ├── __init__.py
    ├── validators.py
    ├── cleaners.py
    └── helpers.py
```

### Core Settings Configuration

```python
# config/settings.py
"""
ResilienceAI Scrapy Settings
Comprehensive configuration for web scraping operations
"""

import os
from datetime import timedelta

# Project Settings
BOT_NAME = 'resilience_scraper'
SPIDER_MODULES = ['resilience_scraper.spiders']
NEWSPIDER_MODULE = 'resilience_scraper.spiders'

# Crawl Settings
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 2
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Retry Configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_DELAY = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]

# Timeout Settings
DOWNLOAD_TIMEOUT = 30
DNS_TIMEOUT = 10

# User Agent Rotation
USER_AGENT_ROTATION_ENABLED = True
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
}

# Cookie Handling
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Pipeline Configuration
ITEM_PIPELINES = {
    'resilience_scraper.pipelines.validation_pipeline.ValidationPipeline': 100,
    'resilience_scraper.pipelines.cleaning_pipeline.CleaningPipeline': 200,
    'resilience_scraper.pipelines.storage_pipeline.MongoDBPipeline': 300,
    'resilience_scraper.pipelines.notification_pipeline.NotificationPipeline': 400,
}

# Middleware Configuration
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'resilience_scraper.middlewares.user_agent_middleware.RotateUserAgentMiddleware': 400,
    'resilience_scraper.middlewares.proxy_middleware.ProxyMiddleware': 350,
    'resilience_scraper.middlewares.rate_limit_middleware.RateLimitMiddleware': 450,
    'resilience_scraper.middlewares.retry_middleware.CustomRetryMiddleware': 550,
    'resilience_scraper.middlewares.captcha_middleware.CaptchaMiddleware': 600,
}

SPIDER_MIDDLEWARES = {
    'resilience_scraper.middlewares.spider_middleware.SpiderErrorMiddleware': 50,
}

# Extensions
EXTENSIONS = {
    'scrapy.extensions.statsmailer.StatsMailer': 500,
    'resilience_scraper.extensions.monitor_extension.MonitorExtension': 600,
}

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(levelname)s: %(message)s'
LOG_FILE = 'logs/scrapy.log'
LOG_ENCODING = 'utf-8'

# Memory Management
MEMDEBUG_ENABLED = True
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512
MEMUSAGE_WARNING_MB = 384

# AutoThrottle (Polite Crawling)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Cache Configuration
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Database Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'resilience_data')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'scraped_items')

POSTGRES_URI = os.getenv('POSTGRES_URI', 'postgresql://user:pass@localhost/resilience')

# Redis Configuration (for distributed crawling)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

# Proxy Configuration
PROXY_ENABLED = True
PROXY_LIST = 'config/proxies.txt'
PROXY_MODE = 0  # 0 = random, 1 = sequential

# CAPTCHA Configuration
CAPTCHA_SERVICE = os.getenv('CAPTCHA_SERVICE', '2captcha')
CAPTCHA_API_KEY = os.getenv('CAPTCHA_API_KEY', '')
CAPTCHA_TIMEOUT = 120

# Notification Settings
NOTIFICATION_ENABLED = True
NOTIFICATION_WEBHOOK = os.getenv('NOTIFICATION_WEBHOOK', '')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')

# Export Settings
FEEDS = {
    'exports/%(name)s/%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 2,
        'item_export_kwargs': {
            'export_empty_fields': True,
        },
    },
    'exports/%(name)s/%(time)s.csv': {
        'format': 'csv',
        'encoding': 'utf8',
    },
}

# Performance Tuning
REACTOR_THREADPOOL_MAXSIZE = 20
DOWNLOAD_HANDLERS = {
    'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
}

# Security
ROBOTSTXT_OBEY = True
ROBOTSTXT_USER_AGENT = 'ResilienceAI-Bot'
```

### Base Spider Implementation

```python
# spiders/base_spider.py
"""
Base Spider for ResilienceAI Scraping
Provides common functionality for all spiders
"""

import logging
from datetime import datetime, timedelta
from typing import Generator, Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy.http import Request, Response
from scrapy.exceptions import CloseSpider, IgnoreRequest

from resilience_scraper.items.news_item import NewsItem
from resilience_scraper.utils.helpers import extract_domain, clean_text


class BaseResilienceSpider(scrapy.Spider):
    """
    Base spider with common functionality for ResilienceAI scraping.
    
    Features:
    - Automatic URL deduplication
    - Rate limiting per domain
    - Error handling and retry logic
    - Data validation hooks
    - Progress tracking
    """
    
    name = 'base_resilience'
    
    # Spider Configuration
    allowed_domains: List[str] = []
    start_urls: List[str] = []
    max_pages: int = 1000
    max_depth: int = 3
    
    # Rate Limiting
    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3,
    }
    
    # Tracking
    pages_crawled: int = 0
    items_extracted: int = 0
    errors_encountered: int = 0
    start_time: Optional[datetime] = None
    
    def __init__(self, **kwargs):
        """Initialize spider with configuration."""
        super().__init__(**kwargs)
        
        # Parse command line arguments
        self.max_pages = int(kwargs.get('max_pages', self.max_pages))
        self.max_depth = int(kwargs.get('max_depth', self.max_depth))
        self.allowed_domains = kwargs.get('allowed_domains', self.allowed_domains)
        
        # Initialize logger
        self.logger = logging.getLogger(self.name)
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'responses_received': 0,
            'items_scraped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def start_requests(self) -> Generator[Request, None, None]:
        """Start the crawling process."""
        self.start_time = datetime.now()
        self.stats['start_time'] = self.start_time.isoformat()
        
        self.logger.info(f"Starting spider: {self.name}")
        self.logger.info(f"Max pages: {self.max_pages}, Max depth: {self.max_depth}")
        
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                meta={'depth': 0},
                dont_filter=False,
            )
    
    def parse(self, response: Response) -> Generator[Any, None, None]:
        """
        Main parsing method. Override in subclasses.
        
        Args:
            response: Scrapy Response object
            
        Yields:
            Items or follow-up requests
        """
        self.pages_crawled += 1
        self.stats['responses_received'] += 1
        
        # Check page limit
        if self.pages_crawled >= self.max_pages:
            self.logger.info(f"Reached max pages limit: {self.max_pages}")
            raise CloseSpider('max_pages_reached')
        
        # Extract data (override in subclass)
        yield from self.extract_data(response)
        
        # Follow links if within depth limit
        current_depth = response.meta.get('depth', 0)
        if current_depth < self.max_depth:
            yield from self.follow_links(response, current_depth)
    
    def extract_data(self, response: Response) -> Generator[Any, None, None]:
        """
        Extract data from response. Override in subclasses.
        
        Args:
            response: Scrapy Response object
            
        Yields:
            Scraped items
        """
        raise NotImplementedError("Subclasses must implement extract_data()")
    
    def follow_links(self, response: Response, current_depth: int) -> Generator[Request, None, None]:
        """
        Follow links found on the page.
        
        Args:
            response: Scrapy Response object
            current_depth: Current crawl depth
            
        Yields:
            Follow-up requests
        """
        links = response.css('a::attr(href)').getall()
        
        for link in links:
            absolute_url = urljoin(response.url, link)
            
            # Validate URL
            if not self.is_valid_url(absolute_url):
                continue
            
            yield Request(
                url=absolute_url,
                callback=self.parse,
                errback=self.handle_error,
                meta={'depth': current_depth + 1},
                priority=10 - current_depth,  # Higher priority for lower depth
            )
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL should be followed.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid for crawling
        """
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check domain
        if self.allowed_domains:
            domain = parsed.netloc.lower()
            if not any(d in domain for d in self.allowed_domains):
                return False
        
        # Skip common non-content URLs
        skip_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', '.mp4']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return True
    
    def handle_error(self, failure) -> None:
        """
        Handle request failures.
        
        Args:
            failure: Twisted Failure object
        """
        self.errors_encountered += 1
        self.stats['errors'] += 1
        
        self.logger.error(f"Request failed: {failure.getErrorMessage()}")
        self.logger.error(f"Failed URL: {failure.request.url}")
        
        # Log detailed error information
        if failure.check(IgnoreRequest):
            self.logger.warning(f"Request ignored: {failure.request.url}")
        else:
            self.logger.error(f"Error type: {failure.type}")
    
    def closed(self, reason: str) -> None:
        """
        Called when spider is closed.
        
        Args:
            reason: Reason for spider closure
        """
        self.stats['end_time'] = datetime.now().isoformat()
        duration = datetime.now() - (self.start_time or datetime.now())
        
        self.logger.info("=" * 50)
        self.logger.info(f"Spider closed: {self.name}")
        self.logger.info(f"Reason: {reason}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Pages crawled: {self.pages_crawled}")
        self.logger.info(f"Items extracted: {self.items_extracted}")
        self.logger.info(f"Errors: {self.errors_encountered}")
        self.logger.info("=" * 50)
        
        # Send notification if configured
        if self.settings.getbool('NOTIFICATION_ENABLED'):
            self.send_notification(reason, duration)
    
    def send_notification(self, reason: str, duration: timedelta) -> None:
        """Send completion notification."""
        # Implementation depends on notification service
        pass
```

### News Spider Example

```python
# spiders/news_spider.py
"""
News Spider for ResilienceAI
Extracts news articles from various news sources
"""

from datetime import datetime
from typing import Generator, Any
from urllib.parse import urljoin

import scrapy
from scrapy.http import Request, Response
from scrapy.selector import Selector

from resilience_scraper.spiders.base_spider import BaseResilienceSpider
from resilience_scraper.items.news_item import NewsItem


class NewsSpider(BaseResilienceSpider):
    """
    Spider for extracting news articles.
    
    Supports:
    - Multiple news sources
    - Article metadata extraction
    - Content parsing
    - Date filtering
    """
    
    name = 'news_spider'
    
    # Source configurations
    sources = {
        'reuters': {
            'start_url': 'https://www.reuters.com/news/archive/worldNews',
            'article_selector': 'article.story',
            'title_selector': 'h3.story-title::text',
            'link_selector': 'a::attr(href)',
            'date_selector': 'time::attr(datetime)',
        },
        'bbc': {
            'start_url': 'https://www.bbc.com/news/world',
            'article_selector': 'div.gs-c-promo',
            'title_selector': 'h3.gs-c-promo-heading__title::text',
            'link_selector': 'a.gs-c-promo-heading::attr(href)',
            'date_selector': 'time::attr(datetime)',
        },
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }
    
    def __init__(self, source: str = None, **kwargs):
        """Initialize with specific source."""
        super().__init__(**kwargs)
        
        self.source = source
        if source and source in self.sources:
            self.start_urls = [self.sources[source]['start_url']]
            self.allowed_domains = [self.sources[source]['start_url'].split('/')[2]]
    
    def start_requests(self) -> Generator[Request, None, None]:
        """Start requests for all configured sources."""
        if self.source:
            yield from super().start_requests()
        else:
            for source_name, config in self.sources.items():
                yield Request(
                    url=config['start_url'],
                    callback=self.parse_source_list,
                    meta={'source': source_name, 'config': config, 'depth': 0},
                )
    
    def parse_source_list(self, response: Response) -> Generator[Any, None, None]:
        """Parse article list from a news source."""
        source = response.meta['source']
        config = response.meta['config']
        
        self.logger.info(f"Parsing {source}: {response.url}")
        
        articles = response.css(config['article_selector'])
        
        for article in articles:
            title = article.css(config['title_selector']).get('')
            link = article.css(config['link_selector]').get('')
            date_str = article.css(config['date_selector']).get('')
            
            if title and link:
                absolute_link = urljoin(response.url, link)
                
                yield Request(
                    url=absolute_link,
                    callback=self.parse_article,
                    meta={
                        'source': source,
                        'title': title.strip(),
                        'date': date_str,
                    },
                )
    
    def parse_article(self, response: Response) -> Generator[NewsItem, None, None]:
        """Parse individual article page."""
        source = response.meta['source']
        title = response.meta.get('title', '')
        date_str = response.meta.get('date', '')
        
        self.logger.info(f"Parsing article: {response.url}")
        
        # Extract content based on source
        content = self.extract_content(response, source)
        
        # Create item
        item = NewsItem()
        item['url'] = response.url
        item['title'] = title or response.css('h1::text').get('')
        item['content'] = content
        item['source'] = source
        item['published_date'] = self.parse_date(date_str)
        item['scraped_date'] = datetime.now().isoformat()
        item['author'] = self.extract_author(response, source)
        item['tags'] = self.extract_tags(response, source)
        
        self.items_extracted += 1
        
        yield item
    
    def extract_content(self, response: Response, source: str) -> str:
        """Extract article content based on source."""
        content_selectors = {
            'reuters': 'div.StandardArticleBody_body p::text',
            'bbc': 'div.ssrcss-uf6wea-RichTextComponentWrapper p::text',
        }
        
        selector = content_selectors.get(source, 'article p::text')
        paragraphs = response.css(selector).getall()
        
        return '\n\n'.join(p.strip() for p in paragraphs if p.strip())
    
    def extract_author(self, response: Response, source: str) -> str:
        """Extract article author."""
        author_selectors = {
            'reuters': 'a.AuthorName::text',
            'bbc': 'span.ssrcss-68dph5-ContributorName::text',
        }
        
        selector = author_selectors.get(source, '.author::text')
        return response.css(selector).get('')
    
    def extract_tags(self, response: Response, source: str) -> list:
        """Extract article tags/categories."""
        tag_selectors = {
            'reuters': 'a[href*="/subjects/"]::text',
            'bbc': 'a[href*="/news/topics/"]::text',
        }
        
        selector = tag_selectors.get(source, 'a.tag::text')
        return response.css(selector).getall()
    
    def parse_date(self, date_str: str) -> str:
        """Parse and normalize date string."""
        if not date_str:
            return datetime.now().isoformat()
        
        # Try common date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%d %B %Y',
            '%B %d, %Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        return date_str
```

### Government Data Spider

```python
# spiders/government_spider.py
"""
Government Data Spider for ResilienceAI
Extracts data from government portals and APIs
"""

import json
from datetime import datetime
from typing import Generator, Any, Dict
from urllib.parse import urlencode, parse_qs, urlparse

import scrapy
from scrapy.http import Request, Response, FormRequest

from resilience_scraper.spiders.base_spider import BaseResilienceSpider
from resilience_scraper.items.document_item import DocumentItem


class GovernmentSpider(BaseResilienceSpider):
    """
    Spider for extracting government data and documents.
    
    Features:
    - API endpoint handling
    - Form-based navigation
    - Document downloads
    - Metadata extraction
    """
    
    name = 'government_spider'
    
    # Government data sources
    sources = {
        'data_gov': {
            'base_url': 'https://catalog.data.gov/api/3',
            'search_endpoint': '/action/package_search',
        },
        'fema': {
            'base_url': 'https://www.fema.gov/api/open',
            'disaster_endpoint': '/v2/DisasterDeclarationsSummaries',
        },
        'usgs': {
            'base_url': 'https://earthquake.usgs.gov/fdsnws/event/1',
            'query_endpoint': '/query',
        },
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3.0,  # Be extra polite to government sites
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': True,
    }
    
    def __init__(self, source: str = None, query: str = None, **kwargs):
        """Initialize government spider."""
        super().__init__(**kwargs)
        self.source = source
        self.query = query or 'disaster emergency resilience'
    
    def start_requests(self) -> Generator[Request, None, None]:
        """Start requests for government data sources."""
        if self.source == 'data_gov':
            yield from self.data_gov_requests()
        elif self.source == 'fema':
            yield from self.fema_requests()
        elif self.source == 'usgs':
            yield from self.usgs_requests()
        else:
            # Query all sources
            yield from self.data_gov_requests()
            yield from self.fema_requests()
            yield from self.usgs_requests()
    
    def data_gov_requests(self) -> Generator[Request, None, None]:
        """Generate requests for data.gov API."""
        base_url = self.sources['data_gov']['base_url']
        endpoint = self.sources['data_gov']['search_endpoint']
        
        params = {
            'q': self.query,
            'rows': 100,
            'start': 0,
        }
        
        url = f"{base_url}{endpoint}?{urlencode(params)}"
        
        yield Request(
            url=url,
            callback=self.parse_data_gov_response,
            meta={'source': 'data_gov', 'params': params},
            headers={'Accept': 'application/json'},
        )
    
    def parse_data_gov_response(self, response: Response) -> Generator[Any, None, None]:
        """Parse data.gov API response."""
        try:
            data = json.loads(response.text)
            results = data.get('result', {}).get('results', [])
            
            for dataset in results:
                item = DocumentItem()
                item['url'] = dataset.get('url', '')
                item['title'] = dataset.get('title', '')
                item['description'] = dataset.get('notes', '')
                item['source'] = 'data.gov'
                item['metadata'] = {
                    'organization': dataset.get('organization', {}).get('title', ''),
                    'tags': [t['name'] for t in dataset.get('tags', [])],
                    'resources': dataset.get('resources', []),
                    'created': dataset.get('metadata_created', ''),
                    'modified': dataset.get('metadata_modified', ''),
                }
                item['scraped_date'] = datetime.now().isoformat()
                
                self.items_extracted += 1
                yield item
            
            # Pagination
            total = data.get('result', {}).get('count', 0)
            params = response.meta['params']
            current_start = params['start']
            
            if current_start + params['rows'] < total:
                params['start'] = current_start + params['rows']
                next_url = f"{self.sources['data_gov']['base_url']}{self.sources['data_gov']['search_endpoint']}?{urlencode(params)}"
                
                yield Request(
                    url=next_url,
                    callback=self.parse_data_gov_response,
                    meta={'source': 'data_gov', 'params': params},
                )
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
    
    def fema_requests(self) -> Generator[Request, None, None]:
        """Generate requests for FEMA API."""
        base_url = self.sources['fema']['base_url']
        endpoint = self.sources['fema']['disaster_endpoint']
        
        params = {
            '$filter': "declarationDate ge '2020-01-01'",
            '$top': 1000,
            '$skip': 0,
        }
        
        url = f"{base_url}{endpoint}?{urlencode(params)}"
        
        yield Request(
            url=url,
            callback=self.parse_fema_response,
            meta={'source': 'fema', 'params': params},
            headers={'Accept': 'application/json'},
        )
    
    def parse_fema_response(self, response: Response) -> Generator[Any, None, None]:
        """Parse FEMA API response."""
        try:
            data = json.loads(response.text)
            disasters = data.get('DisasterDeclarationsSummaries', [])
            
            for disaster in disasters:
                item = DocumentItem()
                item['url'] = f"https://www.fema.gov/disaster/{disaster.get('disasterNumber', '')}"
                item['title'] = f"Disaster {disaster.get('disasterNumber', '')}: {disaster.get('declarationTitle', '')}"
                item['description'] = disaster.get('declarationTitle', '')
                item['source'] = 'fema'
                item['metadata'] = disaster
                item['scraped_date'] = datetime.now().isoformat()
                
                self.items_extracted += 1
                yield item
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FEMA JSON: {e}")
    
    def usgs_requests(self) -> Generator[Request, None, None]:
        """Generate requests for USGS Earthquake API."""
        base_url = self.sources['usgs']['base_url']
        endpoint = self.sources['usgs']['query_endpoint']
        
        params = {
            'format': 'geojson',
            'starttime': '2020-01-01',
            'minmagnitude': 5.0,
            'limit': 1000,
        }
        
        url = f"{base_url}{endpoint}?{urlencode(params)}"
        
        yield Request(
            url=url,
            callback=self.parse_usgs_response,
            meta={'source': 'usgs'},
            headers={'Accept': 'application/geo+json'},
        )
    
    def parse_usgs_response(self, response: Response) -> Generator[Any, None, None]:
        """Parse USGS earthquake data."""
        try:
            data = json.loads(response.text)
            features = data.get('features', [])
            
            for feature in features:
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                item = DocumentItem()
                item['url'] = props.get('url', '')
                item['title'] = props.get('title', '')
                item['description'] = props.get('place', '')
                item['source'] = 'usgs'
                item['metadata'] = {
                    'magnitude': props.get('mag'),
                    'time': props.get('time'),
                    'coordinates': geom.get('coordinates'),
                    'tsunami': props.get('tsunami'),
                    'alert': props.get('alert'),
                    'status': props.get('status'),
                }
                item['scraped_date'] = datetime.now().isoformat()
                
                self.items_extracted += 1
                yield item
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse USGS JSON: {e}")
```


---

## BeautifulSoup Parsing Layer

### BeautifulSoup Integration Module

```python
# utils/parsers.py
"""
BeautifulSoup Parser Utilities for ResilienceAI
Provides advanced HTML parsing capabilities
"""

import re
import logging
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag, NavigableString
from bs4.element import Comment


logger = logging.getLogger(__name__)


class BeautifulSoupParser:
    """
    Advanced BeautifulSoup parser with ResilienceAI-specific utilities.
    
    Features:
    - Content extraction
    - Metadata parsing
    - Table extraction
    - Link analysis
    - Text cleaning
    """
    
    def __init__(self, html: str, parser: str = 'lxml'):
        """
        Initialize parser with HTML content.
        
        Args:
            html: HTML string to parse
            parser: Parser to use ('lxml', 'html.parser', 'html5lib')
        """
        self.soup = BeautifulSoup(html, parser)
        self.original_html = html
    
    @classmethod
    def from_response(cls, response) -> 'BeautifulSoupParser':
        """Create parser from Scrapy response."""
        return cls(response.text)
    
    @classmethod
    def from_file(cls, filepath: str, encoding: str = 'utf-8') -> 'BeautifulSoupParser':
        """Create parser from file."""
        with open(filepath, 'r', encoding=encoding) as f:
            return cls(f.read())
    
    def extract_text(self, 
                     element: Optional[Tag] = None,
                     strip: bool = True,
                     separator: str = ' ') -> str:
        """
        Extract clean text from HTML.
        
        Args:
            element: Specific element to extract from (default: whole document)
            strip: Whether to strip whitespace
            separator: Separator between text elements
            
        Returns:
            Clean text content
        """
        target = element or self.soup
        
        # Remove script and style elements
        for script in target.find_all(['script', 'style', 'nav', 'footer']):
            script.decompose()
        
        # Get text
        text = target.get_text(separator=separator, strip=strip)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_article_content(self) -> Dict[str, Any]:
        """
        Extract article content using common patterns.
        
        Returns:
            Dictionary with title, author, date, content
        """
        result = {
            'title': self.extract_title(),
            'author': self.extract_author(),
            'published_date': self.extract_date(),
            'content': '',
            'summary': '',
        }
        
        # Try multiple content extraction strategies
        content = self._extract_by_article_tag()
        if not content:
            content = self._extract_by_main_tag()
        if not content:
            content = self._extract_by_content_class()
        if not content:
            content = self._extract_by_paragraph_density()
        
        result['content'] = content
        result['summary'] = content[:500] + '...' if len(content) > 500 else content
        
        return result
    
    def _extract_by_article_tag(self) -> str:
        """Extract content from <article> tag."""
        article = self.soup.find('article')
        if article:
            return self.extract_text(article)
        return ''
    
    def _extract_by_main_tag(self) -> str:
        """Extract content from <main> tag."""
        main = self.soup.find('main')
        if main:
            return self.extract_text(main)
        return ''
    
    def _extract_by_content_class(self) -> str:
        """Extract content by common content class names."""
        content_classes = [
            'content', 'article-content', 'post-content',
            'entry-content', 'story-content', 'main-content',
            'article-body', 'post-body', 'entry-body',
        ]
        
        for cls in content_classes:
            element = self.soup.find(class_=re.compile(cls, re.I))
            if element:
                return self.extract_text(element)
        
        return ''
    
    def _extract_by_paragraph_density(self) -> str:
        """Extract content by finding area with highest paragraph density."""
        paragraphs = self.soup.find_all('p')
        
        if not paragraphs:
            return ''
        
        # Find parent with most paragraphs
        parent_counts = {}
        for p in paragraphs:
            parent = p.find_parent(['div', 'section', 'article'])
            if parent:
                parent_id = id(parent)
                parent_counts[parent_id] = parent_counts.get(parent_id, 0) + 1
        
        if parent_counts:
            best_parent_id = max(parent_counts, key=parent_counts.get)
            for p in paragraphs:
                parent = p.find_parent(['div', 'section', 'article'])
                if parent and id(parent) == best_parent_id:
                    return self.extract_text(parent)
        
        # Fallback: join all paragraphs
        return '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)
    
    def extract_title(self) -> str:
        """Extract page title."""
        # Try og:title first
        og_title = self.soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '')
        
        # Try twitter:title
        twitter_title = self.soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title:
            return twitter_title.get('content', '')
        
        # Try h1
        h1 = self.soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Fall back to title tag
        title = self.soup.find('title')
        if title:
            return title.get_text(strip=True)
        
        return ''
    
    def extract_author(self) -> str:
        """Extract article author."""
        # Try common author meta tags
        author_meta = self.soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            return author_meta.get('content', '')
        
        # Try schema.org author
        author = self.soup.find(attrs={'itemprop': 'author'})
        if author:
            return author.get_text(strip=True)
        
        # Try common author class names
        author_classes = ['author', 'byline', 'article-author']
        for cls in author_classes:
            element = self.soup.find(class_=re.compile(cls, re.I))
            if element:
                return element.get_text(strip=True)
        
        return ''
    
    def extract_date(self) -> str:
        """Extract publication date."""
        # Try common date meta tags
        date_meta = self.soup.find('meta', property='article:published_time')
        if date_meta:
            return date_meta.get('content', '')
        
        date_meta = self.soup.find('meta', attrs={'name': 'publishedDate'})
        if date_meta:
            return date_meta.get('content', '')
        
        # Try time element
        time = self.soup.find('time')
        if time:
            return time.get('datetime', '') or time.get_text(strip=True)
        
        # Try schema.org datePublished
        date_published = self.soup.find(attrs={'itemprop': 'datePublished'})
        if date_published:
            return date_published.get('content', '') or date_published.get_text(strip=True)
        
        return ''
    
    def extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extract all tables from the page.
        
        Returns:
            List of table dictionaries with headers and rows
        """
        tables = []
        
        for table in self.soup.find_all('table'):
            table_data = {
                'caption': '',
                'headers': [],
                'rows': [],
            }
            
            # Extract caption
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text(strip=True)
            
            # Extract headers
            thead = table.find('thead')
            if thead:
                headers = thead.find_all('th')
                table_data['headers'] = [h.get_text(strip=True) for h in headers]
            
            # Extract rows
            tbody = table.find('tbody') or table
            for row in tbody.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def extract_links(self, base_url: str = '') -> List[Dict[str, str]]:
        """
        Extract all links from the page.
        
        Args:
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of link dictionaries
        """
        links = []
        
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': link.get_text(strip=True),
                'title': link.get('title', ''),
                'is_external': self._is_external_url(absolute_url, base_url),
            })
        
        return links
    
    def _is_external_url(self, url: str, base_url: str) -> bool:
        """Check if URL is external."""
        if not base_url:
            return False
        
        url_domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc
        
        return url_domain != base_domain
    
    def extract_images(self, base_url: str = '') -> List[Dict[str, str]]:
        """
        Extract all images from the page.
        
        Args:
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of image dictionaries
        """
        images = []
        
        for img in self.soup.find_all('img'):
            src = img.get('src', '')
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    'url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                })
        
        return images
    
    def extract_metadata(self) -> Dict[str, str]:
        """
        Extract all metadata from the page.
        
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'title': self.extract_title(),
            'description': '',
            'keywords': '',
            'author': self.extract_author(),
            'og_tags': {},
            'twitter_tags': {},
        }
        
        # Standard meta tags
        description = self.soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')
        
        keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            metadata['keywords'] = keywords.get('content', '')
        
        # Open Graph tags
        for tag in self.soup.find_all('meta', property=re.compile(r'^og:')):
            prop = tag.get('property', '').replace('og:', '')
            metadata['og_tags'][prop] = tag.get('content', '')
        
        # Twitter Card tags
        for tag in self.soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = tag.get('name', '').replace('twitter:', '')
            metadata['twitter_tags'][name] = tag.get('content', '')
        
        return metadata
    
    def find_by_text(self, text: str, 
                     tag: Optional[str] = None,
                     partial: bool = True) -> List[Tag]:
        """
        Find elements containing specific text.
        
        Args:
            text: Text to search for
            tag: Optional tag name to limit search
            partial: Allow partial matches
            
        Returns:
            List of matching elements
        """
        results = []
        
        if partial:
            pattern = re.compile(re.escape(text), re.I)
        else:
            pattern = re.compile(f'^{re.escape(text)}$', re.I)
        
        if tag:
            elements = self.soup.find_all(tag, string=pattern)
        else:
            elements = self.soup.find_all(string=pattern)
        
        for elem in elements:
            if isinstance(elem, NavigableString):
                results.append(elem.parent)
            else:
                results.append(elem)
        
        return results
    
    def clean_html(self) -> str:
        """
        Clean HTML by removing unwanted elements.
        
        Returns:
            Cleaned HTML string
        """
        # Create a copy
        soup = BeautifulSoup(self.original_html, 'lxml')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 
                                       'aside', 'header', 'advertisement']):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove empty elements
        for element in soup.find_all():
            if len(element.get_text(strip=True)) == 0 and element.name not in ['br', 'hr', 'img']:
                element.decompose()
        
        return str(soup)


class TableExtractor:
    """Specialized table extraction utility."""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def extract_data_tables(self, min_rows: int = 3) -> List[Dict]:
        """
        Extract data-rich tables.
        
        Args:
            min_rows: Minimum rows for a table to be considered data-rich
            
        Returns:
            List of table data
        """
        tables = []
        
        for table in self.soup.find_all('table'):
            data = self._parse_table(table)
            if len(data.get('rows', [])) >= min_rows:
                tables.append(data)
        
        return tables
    
    def _parse_table(self, table: Tag) -> Dict:
        """Parse a single table."""
        result = {
            'caption': '',
            'headers': [],
            'rows': [],
        }
        
        # Caption
        caption = table.find('caption')
        if caption:
            result['caption'] = caption.get_text(strip=True)
        
        # Headers from thead or first row
        thead = table.find('thead')
        if thead:
            result['headers'] = [th.get_text(strip=True) 
                                 for th in thead.find_all('th')]
        
        # Rows
        tbody = table.find('tbody') or table
        rows = tbody.find_all('tr')
        
        # If no headers from thead, use first row
        if not result['headers'] and rows:
            first_row = rows[0]
            result['headers'] = [cell.get_text(strip=True) 
                                 for cell in first_row.find_all(['th', 'td'])]
            rows = rows[1:]
        
        # Process remaining rows
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if any(row_data):  # Skip empty rows
                result['rows'].append(row_data)
        
        return result
    
    def to_dataframe(self, table_data: Dict) -> 'pd.DataFrame':
        """Convert table data to pandas DataFrame."""
        import pandas as pd
        
        df = pd.DataFrame(table_data['rows'], columns=table_data['headers'])
        return df


def parse_html_with_fallback(html: str, 
                              parsers: List[str] = None) -> BeautifulSoup:
    """
    Parse HTML with fallback parsers.
    
    Args:
        html: HTML string
        parsers: List of parsers to try in order
        
    Returns:
        BeautifulSoup object
    """
    parsers = parsers or ['lxml', 'html.parser', 'html5lib']
    
    for parser in parsers:
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            logger.warning(f"Parser {parser} failed: {e}")
            continue
    
    raise ValueError("All parsers failed")
```

---

## Headless Browser Automation

### Playwright Integration

```python
# utils/playwright_driver.py
"""
Playwright Driver for ResilienceAI
Handles JavaScript-heavy sites and dynamic content
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

from playwright.async_api import async_playwright, Page, Browser, BrowserContext


logger = logging.getLogger(__name__)


@dataclass
class BrowserConfig:
    """Configuration for browser instance."""
    headless: bool = True
    slow_mo: int = 50
    timeout: int = 30000
    viewport: Dict[str, int] = None
    user_agent: str = None
    proxy: Dict[str, str] = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {'width': 1920, 'height': 1080}


class PlaywrightDriver:
    """
    Playwright driver for browser automation.
    
    Features:
    - JavaScript execution
    - Dynamic content handling
n    - Screenshot capture
    - PDF generation
    - Form interaction
    """
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self) -> None:
        """Initialize Playwright and browser."""
        self.playwright = await async_playwright().start()
        
        # Launch browser
        browser_args = {
            'headless': self.config.headless,
            'slow_mo': self.config.slow_mo,
        }
        
        if self.config.proxy:
            browser_args['proxy'] = self.config.proxy
        
        self.browser = await self.playwright.chromium.launch(**browser_args)
        
        # Create context
        context_args = {
            'viewport': self.config.viewport,
        }
        
        if self.config.user_agent:
            context_args['user_agent'] = self.config.user_agent
        
        self.context = await self.browser.new_context(**context_args)
        
        logger.info("Playwright browser started")
    
    async def close(self) -> None:
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("Playwright browser closed")
    
    async def new_page(self) -> Page:
        """Create a new page."""
        return await self.context.new_page()
    
    async def navigate(self, url: str, wait_until: str = 'networkidle') -> Page:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
            
        Returns:
            Page object
        """
        page = await self.new_page()
        
        try:
            await page.goto(url, wait_until=wait_until, timeout=self.config.timeout)
            logger.info(f"Navigated to: {url}")
            return page
        except Exception as e:
            await page.close()
            raise e
    
    async def get_content(self, url: str, 
                          wait_for: str = None,
                          scroll: bool = False) -> str:
        """
        Get page content after JavaScript execution.
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for
            scroll: Whether to scroll to bottom
            
        Returns:
            Page HTML content
        """
        page = await self.navigate(url)
        
        try:
            # Wait for specific element if specified
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=self.config.timeout)
            
            # Scroll to bottom if requested
            if scroll:
                await self._scroll_to_bottom(page)
            
            # Wait a bit for any lazy-loaded content
            await asyncio.sleep(1)
            
            content = await page.content()
            return content
        
        finally:
            await page.close()
    
    async def _scroll_to_bottom(self, page: Page) -> None:
        """Scroll to bottom of page."""
        await page.evaluate('''async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    
                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }''')
    
    async def take_screenshot(self, url: str, 
                              output_path: str,
                              full_page: bool = True) -> str:
        """
        Take screenshot of page.
        
        Args:
            url: URL to screenshot
            output_path: Path to save screenshot
            full_page: Whether to capture full page
            
        Returns:
            Path to screenshot file
        """
        page = await self.navigate(url)
        
        try:
            await page.screenshot(path=output_path, full_page=full_page)
            logger.info(f"Screenshot saved: {output_path}")
            return output_path
        finally:
            await page.close()
    
    async def extract_dynamic_content(self, url: str,
                                       extraction_js: str) -> Any:
        """
        Extract content using custom JavaScript.
        
        Args:
            url: URL to fetch
            extraction_js: JavaScript to execute for extraction
            
        Returns:
            Extracted data
        """
        page = await self.navigate(url)
        
        try:
            result = await page.evaluate(extraction_js)
            return result
        finally:
            await page.close()
    
    async def handle_infinite_scroll(self, url: str,
                                      item_selector: str,
                                      max_items: int = 100) -> List[Dict]:
        """
        Handle infinite scroll pages.
        
        Args:
            url: URL to fetch
            item_selector: CSS selector for items
            max_items: Maximum items to collect
            
        Returns:
            List of extracted items
        """
        page = await self.navigate(url)
        items = []
        
        try:
            previous_count = 0
            
            while len(items) < max_items:
                # Get current items
                current_items = await page.query_selector_all(item_selector)
                
                # Extract data from new items
                for i in range(previous_count, len(current_items)):
                    if len(items) >= max_items:
                        break
                    
                    item_data = await current_items[i].evaluate('''element => {
                        return {
                            text: element.textContent,
                            html: element.innerHTML,
                        };
                    }''')
                    items.append(item_data)
                
                # Check if we got new items
                if len(current_items) == previous_count:
                    break
                
                previous_count = len(current_items)
                
                # Scroll down
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            return items
        
        finally:
            await page.close()
    
    async def submit_form(self, url: str,
                          form_selector: str,
                          form_data: Dict[str, str],
                          submit_selector: str = 'button[type="submit"]') -> str:
        """
        Fill and submit a form.
        
        Args:
            url: URL with form
            form_selector: CSS selector for form
            form_data: Dictionary of field names and values
            submit_selector: CSS selector for submit button
            
        Returns:
            Page content after submission
        """
        page = await self.navigate(url)
        
        try:
            # Fill form fields
            for field_name, value in form_data.items():
                selector = f'{form_selector} [name="{field_name}"]'
                await page.fill(selector, value)
            
            # Submit form
            await page.click(submit_selector)
            await page.wait_for_load_state('networkidle')
            
            return await page.content()
        
        finally:
            await page.close()
    
    async def intercept_requests(self, url: str,
                                  intercept_patterns: List[str]) -> List[Dict]:
        """
        Intercept network requests.
        
        Args:
            url: URL to monitor
            intercept_patterns: URL patterns to intercept
            
        Returns:
            List of intercepted requests
        """
        intercepted = []
        page = await self.new_page()
        
        # Set up interception
        async def handle_route(route, request):
            url = request.url
            for pattern in intercept_patterns:
                if pattern in url:
                    intercepted.append({
                        'url': url,
                        'method': request.method,
                        'headers': request.headers,
                        'post_data': request.post_data,
                    })
            await route.continue_()
        
        await page.route('**/*', handle_route)
        
        try:
            await page.goto(url, wait_until='networkidle')
            return intercepted
        finally:
            await page.close()


# Synchronous wrapper for easier use
class SyncPlaywrightDriver:
    """Synchronous wrapper for PlaywrightDriver."""
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self._driver = None
    
    def __enter__(self):
        self._driver = PlaywrightDriver(self.config)
        asyncio.get_event_loop().run_until_complete(self._driver.start())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.get_event_loop().run_until_complete(self._driver.close())
    
    def get_content(self, url: str, **kwargs) -> str:
        """Get page content."""
        return asyncio.get_event_loop().run_until_complete(
            self._driver.get_content(url, **kwargs)
        )
    
    def take_screenshot(self, url: str, output_path: str, **kwargs) -> str:
        """Take screenshot."""
        return asyncio.get_event_loop().run_until_complete(
            self._driver.take_screenshot(url, output_path, **kwargs)
        )
```

### Selenium Integration (Alternative)

```python
# utils/selenium_driver.py
"""
Selenium Driver for ResilienceAI
Alternative browser automation using Selenium
"""

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


logger = logging.getLogger(__name__)


@dataclass
class SeleniumConfig:
    """Configuration for Selenium driver."""
    browser: str = 'chrome'
    headless: bool = True
    window_size: str = '1920,1080'
    user_agent: str = None
    proxy: str = None
    timeout: int = 30
    implicit_wait: int = 10


class SeleniumDriver:
    """
    Selenium driver for browser automation.
    
    Supports Chrome and Firefox with extensive configuration options.
    """
    
    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.driver: Optional[webdriver.Remote] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def start(self) -> None:
        """Initialize WebDriver."""
        if self.config.browser.lower() == 'chrome':
            self.driver = self._create_chrome_driver()
        elif self.config.browser.lower() == 'firefox':
            self.driver = self._create_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser}")
        
        # Configure driver
        self.driver.set_window_size(
            *map(int, self.config.window_size.split(','))
        )
        self.driver.implicitly_wait(self.config.implicit_wait)
        
        logger.info(f"Selenium {self.config.browser} driver started")
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver."""
        options = ChromeOptions()
        
        if self.config.headless:
            options.add_argument('--headless')
        
        # Common options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument(f'--window-size={self.config.window_size}')
        
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
        
        if self.config.proxy:
            options.add_argument(f'--proxy-server={self.config.proxy}')
        
        # Additional preferences
        prefs = {
            'profile.managed_default_content_settings.images': 2,  # Disable images
            'profile.default_content_setting_values.notifications': 2,
        }
        options.add_experimental_option('prefs', prefs)
        
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox WebDriver."""
        options = FirefoxOptions()
        
        if self.config.headless:
            options.add_argument('--headless')
        
        options.add_argument(f'--width={self.config.window_size.split(",")[0]}')
        options.add_argument(f'--height={self.config.window_size.split(",")[1]}')
        
        if self.config.user_agent:
            options.set_preference('general.useragent.override', self.config.user_agent)
        
        if self.config.proxy:
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', self.config.proxy)
        
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def close(self) -> None:
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium driver closed")
    
    def navigate(self, url: str) -> None:
        """Navigate to URL."""
        self.driver.get(url)
        logger.info(f"Navigated to: {url}")
    
    def get_content(self, url: str, 
                    wait_for: str = None,
                    scroll: bool = False) -> str:
        """
        Get page content.
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for
            scroll: Whether to scroll to bottom
            
        Returns:
            Page source
        """
        self.navigate(url)
        
        # Wait for element if specified
        if wait_for:
            try:
                WebDriverWait(self.driver, self.config.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for: {wait_for}")
        
        # Scroll if requested
        if scroll:
            self._scroll_to_bottom()
        
        # Wait for lazy content
        time.sleep(1)
        
        return self.driver.page_source
    
    def _scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        last_height = self.driver.execute_script(
            'return document.body.scrollHeight'
        )
        
        while True:
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            time.sleep(1)
            
            new_height = self.driver.execute_script(
                'return document.body.scrollHeight'
            )
            
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def take_screenshot(self, url: str, output_path: str) -> str:
        """Take screenshot."""
        self.navigate(url)
        self.driver.save_screenshot(output_path)
        logger.info(f"Screenshot saved: {output_path}")
        return output_path
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript."""
        return self.driver.execute_script(script)
    
    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR) -> List:
        """Find elements by selector."""
        return self.driver.find_elements(by, selector)
    
    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        """Click element."""
        element = self.driver.find_element(by, selector)
        element.click()
    
    def fill_form(self, selector: str, value: str, 
                  by: By = By.CSS_SELECTOR) -> None:
        """Fill form field."""
        element = self.driver.find_element(by, selector)
        element.clear()
        element.send_keys(value)
```


---

## Data Extraction Pipelines

### Pipeline Architecture

```python
# pipelines/validation_pipeline.py
"""
Validation Pipeline for ResilienceAI
Validates scraped items before storage
"""

import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

import scrapy
from scrapy.exceptions import DropItem
from pydantic import BaseModel, ValidationError, validator


logger = logging.getLogger(__name__)


class NewsItemModel(BaseModel):
    """Pydantic model for news item validation."""
    url: str
    title: str
    content: str
    source: str
    published_date: Optional[str] = None
    scraped_date: str
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Content must be at least 50 characters')
        return v.strip()


class DocumentItemModel(BaseModel):
    """Pydantic model for document item validation."""
    url: str
    title: str
    description: str
    source: str
    metadata: Dict[str, Any]
    scraped_date: str


class ValidationPipeline:
    """
    Pipeline for validating scraped items.
    
    Uses Pydantic models for strict validation.
    Drops invalid items and logs errors.
    """
    
    def __init__(self):
        self.validators = {
            'NewsItem': NewsItemModel,
            'DocumentItem': DocumentItemModel,
        }
        self.stats = {
            'validated': 0,
            'dropped': 0,
            'errors': [],
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def process_item(self, item: Dict, spider: scrapy.Spider) -> Dict:
        """
        Process and validate item.
        
        Args:
            item: Scraped item
            spider: Spider instance
            
        Returns:
            Validated item
            
        Raises:
            DropItem: If validation fails
        """
        item_type = item.__class__.__name__
        
        # Get validator for item type
        validator_class = self.validators.get(item_type)
        
        if not validator_class:
            logger.warning(f"No validator for item type: {item_type}")
            return item
        
        try:
            # Convert item to dict if needed
            item_dict = dict(item)
            
            # Validate
            validated = validator_class(**item_dict)
            
            self.stats['validated'] += 1
            spider.crawler.stats.inc_value('validation/passed')
            
            # Return validated data
            return validated.dict()
        
        except ValidationError as e:
            self.stats['dropped'] += 1
            spider.crawler.stats.inc_value('validation/failed')
            
            error_msg = f"Validation failed for {item_type}: {e}"
            logger.warning(error_msg)
            self.stats['errors'].append({
                'item': item_dict,
                'errors': e.errors(),
            })
            
            raise DropItem(error_msg)


# pipelines/cleaning_pipeline.py
"""
Data Cleaning Pipeline for ResilienceAI
Cleans and normalizes scraped data
"""

import re
import html
from typing import Dict, Any

import scrapy


class CleaningPipeline:
    """
    Pipeline for cleaning scraped data.
    
    Performs:
    - HTML entity decoding
    - Whitespace normalization
    - Text deduplication
    - URL normalization
    """
    
    def process_item(self, item: Dict, spider: scrapy.Spider) -> Dict:
        """Clean item data."""
        cleaned = {}
        
        for key, value in item.items():
            if isinstance(value, str):
                cleaned[key] = self.clean_text(value)
            elif isinstance(value, list):
                cleaned[key] = [self.clean_text(v) if isinstance(v, str) else v 
                               for v in value]
            elif isinstance(value, dict):
                cleaned[key] = {k: self.clean_text(v) if isinstance(v, str) else v 
                               for k, v in value.items()}
            else:
                cleaned[key] = value
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """Clean text content."""
        if not text:
            return ''
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove zero-width characters
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        
        return text.strip()


# pipelines/storage_pipeline.py
"""
Storage Pipeline for ResilienceAI
Handles data persistence to multiple backends
"""

import logging
from typing import Dict, Any
from datetime import datetime

import scrapy
import pymongo
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import DuplicateKeyError, ConnectionFailure


logger = logging.getLogger(__name__)


class MongoDBPipeline:
    """
    Pipeline for storing items in MongoDB.
    
    Features:
    - Connection pooling
    - Duplicate detection
    - Index management
    - Bulk operations
    """
    
    def __init__(self, mongo_uri: str, database: str, collection: str):
        self.mongo_uri = mongo_uri
        self.database = database
        self.collection = collection
        self.client = None
        self.db = None
        self.col = None
        self.buffer = []
        self.buffer_size = 100
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            database=crawler.settings.get('MONGODB_DATABASE'),
            collection=crawler.settings.get('MONGODB_COLLECTION'),
        )
    
    def open_spider(self, spider: scrapy.Spider) -> None:
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database]
            self.col = self.db[self.collection]
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB: {self.database}.{self.collection}")
        
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def close_spider(self, spider: scrapy.Spider) -> None:
        """Close MongoDB connection and flush buffer."""
        # Flush remaining items
        if self.buffer:
            self._insert_bulk()
        
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def _create_indexes(self) -> None:
        """Create database indexes."""
        # Unique index on URL
        self.col.create_index('url', unique=True)
        
        # Text index for search
        self.col.create_index([('title', TEXT), ('content', TEXT)])
        
        # Date indexes
        self.col.create_index('scraped_date')
        self.col.create_index('published_date')
        
        # Source index
        self.col.create_index('source')
    
    def process_item(self, item: Dict, spider: scrapy.Spider) -> Dict:
        """Process and store item."""
        # Add metadata
        item['stored_at'] = datetime.now().isoformat()
        item['spider'] = spider.name
        
        # Add to buffer
        self.buffer.append(item)
        
        # Flush if buffer is full
        if len(self.buffer) >= self.buffer_size:
            self._insert_bulk()
        
        return item
    
    def _insert_bulk(self) -> None:
        """Insert buffered items in bulk."""
        if not self.buffer:
            return
        
        try:
            # Use ordered=False to continue on errors
            result = self.col.insert_many(self.buffer, ordered=False)
            logger.debug(f"Inserted {len(result.inserted_ids)} items")
        
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error: {e}")
        
        except Exception as e:
            logger.error(f"Bulk insert error: {e}")
        
        finally:
            self.buffer = []


class PostgreSQLPipeline:
    """
    Pipeline for storing items in PostgreSQL.
    
    Uses SQLAlchemy for ORM operations.
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.Session = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            connection_string=crawler.settings.get('POSTGRES_URI')
        )
    
    def open_spider(self, spider: scrapy.Spider) -> None:
        """Initialize database connection."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        logger.info("PostgreSQL connection established")
    
    def close_spider(self, spider: scrapy.Spider) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL connection closed")
    
    def process_item(self, item: Dict, spider: scrapy.Spider) -> Dict:
        """Store item in PostgreSQL."""
        session = self.Session()
        
        try:
            # Convert item to ORM model
            record = ScrapedItem(
                url=item['url'],
                title=item.get('title', ''),
                content=item.get('content', ''),
                source=item.get('source', ''),
                scraped_at=datetime.now(),
                metadata=item.get('metadata', {}),
            )
            
            session.add(record)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
        
        finally:
            session.close()
        
        return item


# pipelines/notification_pipeline.py
"""
Notification Pipeline for ResilienceAI
Sends notifications on important events
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime

import requests
import scrapy


logger = logging.getLogger(__name__)


class NotificationPipeline:
    """
    Pipeline for sending notifications.
    
    Supports:
    - Webhook notifications
    - Email notifications
    - Slack notifications
    """
    
    def __init__(self, webhook_url: str = None, email: str = None):
        self.webhook_url = webhook_url
        self.email = email
        self.notification_threshold = 100  # Notify every N items
        self.item_count = 0
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            webhook_url=crawler.settings.get('NOTIFICATION_WEBHOOK'),
            email=crawler.settings.get('NOTIFICATION_EMAIL'),
        )
    
    def process_item(self, item: Dict, spider: scrapy.Spider) -> Dict:
        """Process item and send notifications if needed."""
        self.item_count += 1
        
        # Send periodic notifications
        if self.item_count % self.notification_threshold == 0:
            self.send_progress_notification(spider)
        
        return item
    
    def send_progress_notification(self, spider: scrapy.Spider) -> None:
        """Send progress notification."""
        message = {
            'spider': spider.name,
            'items_processed': self.item_count,
            'timestamp': datetime.now().isoformat(),
        }
        
        if self.webhook_url:
            self._send_webhook(message)
    
    def _send_webhook(self, message: Dict) -> None:
        """Send webhook notification."""
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10,
            )
            response.raise_for_status()
        
        except requests.RequestException as e:
            logger.error(f"Webhook notification failed: {e}")
    
    def close_spider(self, spider: scrapy.Spider) -> None:
        """Send completion notification."""
        message = {
            'event': 'spider_closed',
            'spider': spider.name,
            'total_items': self.item_count,
            'timestamp': datetime.now().isoformat(),
        }
        
        if self.webhook_url:
            self._send_webhook(message)
```

---

## Rate Limiting & Politeness

### Rate Limit Middleware

```python
# middlewares/rate_limit_middleware.py
"""
Rate Limit Middleware for ResilienceAI
Implements polite crawling with adaptive rate limiting
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.exceptions import IgnoreRequest


logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware for rate limiting requests.
    
    Features:
    - Per-domain rate limiting
    - Adaptive delay adjustment
    - 429 response handling
    - Retry-After header support
    """
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        
        # Base delay settings
        self.base_delay = self.settings.getfloat('DOWNLOAD_DELAY', 1.0)
        self.randomize_delay = self.settings.getbool('RANDOMIZE_DOWNLOAD_DELAY', True)
        
        # Domain-specific delays
        self.domain_delays: Dict[str, float] = {}
        self.last_request_time: Dict[str, float] = defaultdict(float)
        
        # Error tracking
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.consecutive_errors: Dict[str, int] = defaultdict(int)
        
        # Adaptive settings
        self.adaptive_enabled = True
        self.min_delay = 0.5
        self.max_delay = 60.0
        self.delay_increase_factor = 1.5
        self.delay_decrease_factor = 0.9
        
        # 429 handling
        self.rate_limited_domains: Dict[str, datetime] = {}
        self.rate_limit_cooldown = timedelta(minutes=5)
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        """Initialize spider-specific settings."""
        # Check for spider-specific delays
        if hasattr(spider, 'custom_settings'):
            spider_delay = spider.custom_settings.get('DOWNLOAD_DELAY')
            if spider_delay:
                self.base_delay = spider_delay
        
        logger.info(f"Rate limit middleware initialized with delay: {self.base_delay}s")
    
    def process_request(self, request: Request, spider) -> Optional[Request]:
        """
        Process outgoing request with rate limiting.
        
        Args:
            request: Outgoing request
            spider: Spider instance
            
        Returns:
            Request or None
        """
        domain = self._get_domain(request.url)
        
        # Check if domain is rate limited
        if self._is_rate_limited(domain):
            retry_after = self._get_retry_after(domain)
            logger.warning(f"Domain {domain} is rate limited. Retry after: {retry_after}")
            raise IgnoreRequest(f"Rate limited. Retry after: {retry_after}")
        
        # Calculate delay
        delay = self._get_delay(domain)
        
        # Enforce delay
        last_request = self.last_request_time[domain]
        elapsed = time.time() - last_request
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s for {domain}")
            time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()
        
        return None
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        """
        Process response and adjust rate limits.
        
        Args:
            request: Original request
            response: Received response
            spider: Spider instance
            
        Returns:
            Response
        """
        domain = self._get_domain(request.url)
        
        # Handle 429 Too Many Requests
        if response.status == 429:
            self._handle_rate_limit_response(domain, response)
        
        # Handle server errors
        elif response.status >= 500:
            self._handle_server_error(domain)
        
        # Handle success
        elif response.status == 200:
            self._handle_success(domain)
        
        return response
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
    
    def _get_delay(self, domain: str) -> float:
        """Get delay for domain."""
        delay = self.domain_delays.get(domain, self.base_delay)
        
        if self.randomize_delay:
            import random
            delay = random.uniform(delay * 0.5, delay * 1.5)
        
        return delay
    
    def _is_rate_limited(self, domain: str) -> bool:
        """Check if domain is currently rate limited."""
        if domain not in self.rate_limited_domains:
            return False
        
        limited_until = self.rate_limited_domains[domain]
        return datetime.now() < limited_until
    
    def _get_retry_after(self, domain: str) -> datetime:
        """Get retry time for rate limited domain."""
        return self.rate_limited_domains.get(domain, datetime.now())
    
    def _handle_rate_limit_response(self, domain: str, response: Response) -> None:
        """Handle 429 response."""
        # Check for Retry-After header
        retry_after = response.headers.get('Retry-After')
        
        if retry_after:
            try:
                # Try parsing as seconds
                seconds = int(retry_after)
                cooldown = timedelta(seconds=seconds)
            except ValueError:
                # Try parsing as HTTP date
                try:
                    from email.utils import parsedate_to_datetime
                    retry_date = parsedate_to_datetime(retry_after)
                    cooldown = retry_date - datetime.now()
                except:
                    cooldown = self.rate_limit_cooldown
        else:
            cooldown = self.rate_limit_cooldown
        
        self.rate_limited_domains[domain] = datetime.now() + cooldown
        
        # Increase delay
        current_delay = self.domain_delays.get(domain, self.base_delay)
        new_delay = min(current_delay * self.delay_increase_factor, self.max_delay)
        self.domain_delays[domain] = new_delay
        
        logger.warning(f"Rate limited on {domain}. New delay: {new_delay:.2f}s")
    
    def _handle_server_error(self, domain: str) -> None:
        """Handle server error response."""
        self.consecutive_errors[domain] += 1
        
        # Increase delay if multiple consecutive errors
        if self.consecutive_errors[domain] >= 3:
            current_delay = self.domain_delays.get(domain, self.base_delay)
            new_delay = min(current_delay * self.delay_increase_factor, self.max_delay)
            self.domain_delays[domain] = new_delay
            
            logger.warning(
                f"Multiple errors on {domain}. Increasing delay to {new_delay:.2f}s"
            )
    
    def _handle_success(self, domain: str) -> None:
        """Handle successful response."""
        # Reset error count
        self.consecutive_errors[domain] = 0
        
        # Gradually decrease delay
        if self.adaptive_enabled:
            current_delay = self.domain_delays.get(domain, self.base_delay)
            if current_delay > self.base_delay:
                new_delay = max(
                    current_delay * self.delay_decrease_factor,
                    self.base_delay
                )
                self.domain_delays[domain] = new_delay


# middlewares/retry_middleware.py
"""
Custom Retry Middleware for ResilienceAI
Enhanced retry logic with exponential backoff
"""

import logging
from typing import Optional

from scrapy.downloadermiddlewares.retry import RetryMiddleware as BaseRetryMiddleware
from scrapy.http import Request, Response
from scrapy.utils.response import response_status_message


logger = logging.getLogger(__name__)


class CustomRetryMiddleware(BaseRetryMiddleware):
    """
    Enhanced retry middleware with:
    - Exponential backoff
    - Smart retry conditions
    - Detailed logging
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(settings.getlist('RETRY_HTTP_CODES', 
                                                       [500, 502, 503, 504, 408, 429]))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST', -1)
        
        # Exponential backoff settings
        self.backoff_base = 2
        self.max_backoff = 300  # 5 minutes
    
    def process_response(self, request: Request, response: Response, spider):
        """Process response and retry if needed."""
        if request.meta.get('dont_retry', False):
            return response
        
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        
        return response
    
    def _retry(self, request: Request, reason: str, spider):
        """Retry request with exponential backoff."""
        retries = request.meta.get('retry_times', 0) + 1
        
        if retries <= self.max_retry_times:
            logger.debug(f"Retrying {request} (failed {retries} times): {reason}")
            
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            
            # Calculate backoff delay
            backoff = min(
                self.backoff_base ** retries,
                self.max_backoff
            )
            retryreq.meta['download_delay'] = backoff
            
            logger.info(
                f"Retry {retries}/{self.max_retry_times} for {request.url} "
                f"(backoff: {backoff}s)"
            )
            
            return retryreq
        
        else:
            logger.error(
                f"Gave up retrying {request} (failed {retries} times): {reason}"
            )
            return None
```

---

## Proxy Rotation System

### Proxy Middleware

```python
# middlewares/proxy_middleware.py
"""
Proxy Middleware for ResilienceAI
Manages proxy rotation and health checking
"""

import logging
import random
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from scrapy.http import Request, Response


logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """Proxy configuration."""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'
    country: Optional[str] = None
    
    # Health tracking
    success_count: int = 0
    fail_count: int = 0
    last_used: Optional[datetime] = None
    last_failed: Optional[datetime] = None
    is_banned: bool = False
    
    @property
    def meta_url(self) -> str:
        """Get proxy URL for Scrapy meta."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.url}"
        return f"{self.protocol}://{self.url}"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.fail_count
        if total == 0:
            return 1.0
        return self.success_count / total


class ProxyManager:
    """
    Manages proxy pool with health tracking.
    
    Features:
    - Proxy rotation strategies
    - Health checking
    - Ban detection
    - Automatic failover
    """
    
    def __init__(self):
        self.proxies: List[Proxy] = []
        self.banned_proxies: Set[str] = set()
        self.domain_proxies: Dict[str, Proxy] = {}
        
        # Rotation strategy
        self.rotation_mode = 'random'  # random, round_robin, least_used
        self._round_robin_index = 0
        
        # Health check settings
        self.health_check_interval = timedelta(minutes=5)
        self.min_success_rate = 0.5
        self.max_failures = 5
    
    def add_proxy(self, proxy: Proxy) -> None:
        """Add proxy to pool."""
        self.proxies.append(proxy)
        logger.debug(f"Added proxy: {proxy.url}")
    
    def add_proxies_from_file(self, filepath: str) -> None:
        """Load proxies from file."""
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.add_proxy(Proxy(url=line))
    
    def add_proxies_from_api(self, api_url: str, api_key: str) -> None:
        """Fetch proxies from proxy provider API."""
        try:
            response = requests.get(
                api_url,
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            for proxy_data in data.get('proxies', []):
                proxy = Proxy(
                    url=proxy_data['url'],
                    username=proxy_data.get('username'),
                    password=proxy_data.get('password'),
                    protocol=proxy_data.get('protocol', 'http'),
                    country=proxy_data.get('country'),
                )
                self.add_proxy(proxy)
            
            logger.info(f"Loaded {len(data.get('proxies', []))} proxies from API")
        
        except requests.RequestException as e:
            logger.error(f"Failed to fetch proxies from API: {e}")
    
    def get_proxy(self, domain: str = None) -> Optional[Proxy]:
        """
        Get next proxy based on rotation strategy.
        
        Args:
            domain: Domain to get proxy for (for sticky sessions)
            
        Returns:
            Proxy instance or None
        """
        # Check for sticky session
        if domain and domain in self.domain_proxies:
            proxy = self.domain_proxies[domain]
            if not proxy.is_banned:
                return proxy
        
        # Filter available proxies
        available = [p for p in self.proxies if not p.is_banned]
        
        if not available:
            logger.warning("No available proxies")
            return None
        
        # Select based on rotation mode
        if self.rotation_mode == 'random':
            proxy = random.choice(available)
        
        elif self.rotation_mode == 'round_robin':
            proxy = available[self._round_robin_index % len(available)]
            self._round_robin_index += 1
        
        elif self.rotation_mode == 'least_used':
            proxy = min(available, key=lambda p: p.success_count + p.fail_count)
        
        elif self.rotation_mode == 'best_success_rate':
            proxy = max(available, key=lambda p: p.success_rate)
        
        else:
            proxy = random.choice(available)
        
        # Update sticky session
        if domain:
            self.domain_proxies[domain] = proxy
        
        proxy.last_used = datetime.now()
        
        return proxy
    
    def report_success(self, proxy_url: str) -> None:
        """Report successful request."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.success_count += 1
                break
    
    def report_failure(self, proxy_url: str, error_type: str = 'unknown') -> None:
        """Report failed request."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count += 1
                proxy.last_failed = datetime.now()
                
                # Check if proxy should be banned
                if proxy.fail_count >= self.max_failures:
                    if proxy.success_rate < self.min_success_rate:
                        proxy.is_banned = True
                        self.banned_proxies.add(proxy_url)
                        logger.warning(f"Banned proxy: {proxy_url}")
                
                break
    
    def health_check(self) -> None:
        """Run health check on all proxies."""
        test_url = 'http://httpbin.org/ip'
        
        for proxy in self.proxies:
            if proxy.is_banned:
                # Try to unban after cooldown
                if proxy.last_failed:
                    cooldown = timedelta(minutes=30)
                    if datetime.now() - proxy.last_failed > cooldown:
                        proxy.is_banned = False
                        proxy.fail_count = 0
                        logger.info(f"Unbanned proxy: {proxy.url}")
                continue
            
            try:
                response = requests.get(
                    test_url,
                    proxies={'http': proxy.meta_url, 'https': proxy.meta_url},
                    timeout=10
                )
                
                if response.status_code == 200:
                    proxy.success_count += 1
                else:
                    proxy.fail_count += 1
            
            except requests.RequestException:
                proxy.fail_count += 1


class ProxyMiddleware:
    """
    Scrapy middleware for proxy rotation.
    """
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        
        # Initialize proxy manager
        self.proxy_manager = ProxyManager()
        
        # Load proxies
        proxy_file = self.settings.get('PROXY_LIST')
        if proxy_file:
            self.proxy_manager.add_proxies_from_file(proxy_file)
        
        # Settings
        self.enabled = self.settings.getbool('PROXY_ENABLED', True)
        self.mode = self.settings.getint('PROXY_MODE', 0)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_request(self, request: Request, spider) -> None:
        """Add proxy to request."""
        if not self.enabled:
            return None
        
        # Skip if proxy already set
        if 'proxy' in request.meta:
            return None
        
        # Get domain for sticky session
        from urllib.parse import urlparse
        domain = urlparse(request.url).netloc
        
        # Get proxy
        proxy = self.proxy_manager.get_proxy(domain)
        
        if proxy:
            request.meta['proxy'] = proxy.meta_url
            request.meta['_proxy_url'] = proxy.url
            logger.debug(f"Using proxy {proxy.url} for {request.url}")
        
        return None
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        """Process response and track proxy performance."""
        proxy_url = request.meta.get('_proxy_url')
        
        if proxy_url:
            if response.status < 400:
                self.proxy_manager.report_success(proxy_url)
            else:
                self.proxy_manager.report_failure(proxy_url, f'status_{response.status}')
        
        return response
    
    def process_exception(self, request: Request, exception, spider):
        """Handle request exception."""
        proxy_url = request.meta.get('_proxy_url')
        
        if proxy_url:
            error_type = type(exception).__name__
            self.proxy_manager.report_failure(proxy_url, error_type)
            
            logger.warning(f"Proxy {proxy_url} failed: {error_type}")
        
        return None
```


---

## CAPTCHA Handling

### CAPTCHA Middleware

```python
# middlewares/captcha_middleware.py
"""
CAPTCHA Handling Middleware for ResilienceAI
Detects and solves various CAPTCHA types
"""

import logging
import time
from typing import Optional, Dict, Any
from enum import Enum

import requests
from scrapy.http import Request, Response, HtmlResponse
from scrapy.exceptions import IgnoreRequest


logger = logging.getLogger(__name__)


class CaptchaType(Enum):
    """Types of CAPTCHAs."""
    RECAPTCHA_V2 = 'recaptcha_v2'
    RECAPTCHA_V3 = 'recaptcha_v3'
    HCAPTCHA = 'hcaptcha'
    IMAGE_CAPTCHA = 'image_captcha'
    TEXT_CAPTCHA = 'text_captcha'
    UNKNOWN = 'unknown'


class CaptchaSolver:
    """
    Base class for CAPTCHA solving services.
    """
    
    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve CAPTCHA and return solution."""
        raise NotImplementedError


class TwoCaptchaSolver(CaptchaSolver):
    """
    2captcha.com integration.
    """
    
    API_URL = 'http://2captcha.com'
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve CAPTCHA using 2captcha."""
        captcha_type = captcha_data.get('type')
        
        if captcha_type == CaptchaType.RECAPTCHA_V2:
            return self._solve_recaptcha_v2(captcha_data)
        elif captcha_type == CaptchaType.HCAPTCHA:
            return self._solve_hcaptcha(captcha_data)
        elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
            return self._solve_image_captcha(captcha_data)
        
        return None
    
    def _solve_recaptcha_v2(self, data: Dict) -> Optional[str]:
        """Solve reCAPTCHA v2."""
        # Submit CAPTCHA
        submit_url = f"{self.API_URL}/in.php"
        payload = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': data['sitekey'],
            'pageurl': data['pageurl'],
            'json': 1,
        }
        
        response = requests.post(submit_url, data=payload, timeout=30)
        result = response.json()
        
        if result.get('status') != 1:
            logger.error(f"CAPTCHA submit failed: {result}")
            return None
        
        captcha_id = result.get('request')
        
        # Poll for solution
        return self._poll_solution(captcha_id)
    
    def _solve_hcaptcha(self, data: Dict) -> Optional[str]:
        """Solve hCaptcha."""
        submit_url = f"{self.API_URL}/in.php"
        payload = {
            'key': self.api_key,
            'method': 'hcaptcha',
            'sitekey': data['sitekey'],
            'pageurl': data['pageurl'],
            'json': 1,
        }
        
        response = requests.post(submit_url, data=payload, timeout=30)
        result = response.json()
        
        if result.get('status') != 1:
            logger.error(f"hCaptcha submit failed: {result}")
            return None
        
        return self._poll_solution(result.get('request'))
    
    def _solve_image_captcha(self, data: Dict) -> Optional[str]:
        """Solve image CAPTCHA."""
        submit_url = f"{self.API_URL}/in.php"
        
        files = {'file': ('captcha.jpg', data['image_data'])}
        payload = {
            'key': self.api_key,
            'method': 'post',
            'json': 1,
        }
        
        response = requests.post(submit_url, data=payload, files=files, timeout=30)
        result = response.json()
        
        if result.get('status') != 1:
            logger.error(f"Image CAPTCHA submit failed: {result}")
            return None
        
        return self._poll_solution(result.get('request'))
    
    def _poll_solution(self, captcha_id: str, max_wait: int = 180) -> Optional[str]:
        """Poll for CAPTCHA solution."""
        result_url = f"{self.API_URL}/res.php"
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            time.sleep(5)
            
            response = requests.get(result_url, params={
                'key': self.api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1,
            }, timeout=30)
            
            result = response.json()
            
            if result.get('status') == 1:
                return result.get('request')
            
            if result.get('request') != 'CAPCHA_NOT_READY':
                logger.error(f"CAPTCHA solving error: {result}")
                return None
        
        logger.error("CAPTCHA solving timeout")
        return None


class AntiCaptchaSolver(CaptchaSolver):
    """
    Anti-Captcha.com integration.
    """
    
    API_URL = 'https://api.anti-captcha.com'
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve CAPTCHA using Anti-Captcha."""
        captcha_type = captcha_data.get('type')
        
        # Create task
        create_url = f"{self.API_URL}/createTask"
        
        task = self._create_task(captcha_type, captcha_data)
        
        payload = {
            'clientKey': self.api_key,
            'task': task,
        }
        
        response = requests.post(create_url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('errorId') != 0:
            logger.error(f"Anti-Captcha task creation failed: {result}")
            return None
        
        task_id = result.get('taskId')
        
        # Poll for solution
        return self._poll_solution(task_id)
    
    def _create_task(self, captcha_type: CaptchaType, data: Dict) -> Dict:
        """Create task payload for CAPTCHA type."""
        if captcha_type == CaptchaType.RECAPTCHA_V2:
            return {
                'type': 'NoCaptchaTaskProxyless',
                'websiteURL': data['pageurl'],
                'websiteKey': data['sitekey'],
            }
        elif captcha_type == CaptchaType.HCAPTCHA:
            return {
                'type': 'HCaptchaTaskProxyless',
                'websiteURL': data['pageurl'],
                'websiteKey': data['sitekey'],
            }
        elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
            return {
                'type': 'ImageToTextTask',
                'body': data['image_base64'],
            }
        
        return {}
    
    def _poll_solution(self, task_id: str, max_wait: int = 180) -> Optional[str]:
        """Poll for task solution."""
        result_url = f"{self.API_URL}/getTaskResult"
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            time.sleep(5)
            
            response = requests.post(result_url, json={
                'clientKey': self.api_key,
                'taskId': task_id,
            }, timeout=30)
            
            result = response.json()
            
            if result.get('status') == 'ready':
                return result.get('solution', {}).get('gRecaptchaResponse') or \
                       result.get('solution', {}).get('text')
            
            if result.get('errorId') != 0:
                logger.error(f"Anti-Captcha error: {result}")
                return None
        
        logger.error("Anti-Captcha solving timeout")
        return None


class CaptchaMiddleware:
    """
    Middleware for detecting and solving CAPTCHAs.
    """
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        
        # Initialize solver
        service = self.settings.get('CAPTCHA_SERVICE', '2captcha')
        api_key = self.settings.get('CAPTCHA_API_KEY', '')
        
        if service == '2captcha':
            self.solver = TwoCaptchaSolver(api_key)
        elif service == 'anticaptcha':
            self.solver = AntiCaptchaSolver(api_key)
        else:
            self.solver = None
        
        # Settings
        self.enabled = bool(api_key)
        self.max_attempts = 3
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        """Detect and handle CAPTCHAs in responses."""
        if not self.enabled:
            return response
        
        # Detect CAPTCHA
        captcha_type = self._detect_captcha(response)
        
        if captcha_type:
            logger.warning(f"CAPTCHA detected: {captcha_type} on {response.url}")
            
            # Extract CAPTCHA data
            captcha_data = self._extract_captcha_data(response, captcha_type)
            
            if captcha_data:
                # Solve CAPTCHA
                solution = self.solver.solve(captcha_data)
                
                if solution:
                    # Create new request with solution
                    new_request = self._create_solved_request(
                        request, response, captcha_type, solution
                    )
                    
                    if new_request:
                        return self.crawler.engine.download(new_request, spider)
                
                else:
                    logger.error(f"Failed to solve CAPTCHA on {response.url}")
        
        return response
    
    def _detect_captcha(self, response: Response) -> Optional[CaptchaType]:
        """Detect CAPTCHA type in response."""
        text = response.text.lower()
        
        # Check for reCAPTCHA
        if 'g-recaptcha' in text or 'recaptcha' in text:
            if 'data-size="invisible"' in text:
                return CaptchaType.RECAPTCHA_V3
            return CaptchaType.RECAPTCHA_V2
        
        # Check for hCaptcha
        if 'h-captcha' in text or 'hcaptcha' in text:
            return CaptchaType.HCAPTCHA
        
        # Check for image CAPTCHA
        if response.css('img[src*="captcha"]'):
            return CaptchaType.IMAGE_CAPTCHA
        
        # Check for text CAPTCHA
        if 'captcha' in text and response.css('input[name*="captcha"]'):
            return CaptchaType.TEXT_CAPTCHA
        
        return None
    
    def _extract_captcha_data(self, response: Response, 
                              captcha_type: CaptchaType) -> Optional[Dict]:
        """Extract CAPTCHA solving data from response."""
        data = {
            'type': captcha_type,
            'pageurl': response.url,
        }
        
        if captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.RECAPTCHA_V3]:
            sitekey = response.css('[data-sitekey]::attr(data-sitekey)').get()
            if not sitekey:
                # Try to find in scripts
                import re
                match = re.search(r'sitekey["\']?\s*:\s*["\']([^"\']+)', response.text)
                if match:
                    sitekey = match.group(1)
            
            if sitekey:
                data['sitekey'] = sitekey
                return data
        
        elif captcha_type == CaptchaType.HCAPTCHA:
            sitekey = response.css('[data-sitekey]::attr(data-sitekey)').get()
            if sitekey:
                data['sitekey'] = sitekey
                return data
        
        elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
            img_url = response.css('img[src*="captcha"]::attr(src)').get()
            if img_url:
                # Download image
                img_response = requests.get(
                    response.urljoin(img_url),
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=30
                )
                data['image_data'] = img_response.content
                data['image_base64'] = base64.b64encode(img_response.content).decode()
                return data
        
        return None
    
    def _create_solved_request(self, request: Request, response: Response,
                               captcha_type: CaptchaType, 
                               solution: str) -> Optional[Request]:
        """Create request with CAPTCHA solution."""
        # For reCAPTCHA/hCaptcha, add solution to form
        if captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.HCAPTCHA]:
            # Find form
            form = response.css('form')
            if form:
                # Create form request with solution
                formdata = {}
                
                # Add all form fields
                for input_field in form.css('input'):
                    name = input_field.css('::attr(name)').get()
                    value = input_field.css('::attr(value)').get()
                    if name:
                        formdata[name] = value or ''
                
                # Add CAPTCHA response
                if captcha_type == CaptchaType.RECAPTCHA_V2:
                    formdata['g-recaptcha-response'] = solution
                elif captcha_type == CaptchaType.HCAPTCHA:
                    formdata['h-captcha-response'] = solution
                
                # Create form request
                action = form.css('::attr(action)').get() or ''
                method = form.css('::attr(method)').get() or 'POST'
                
                from scrapy.http import FormRequest
                return FormRequest(
                    url=response.urljoin(action),
                    formdata=formdata,
                    method=method.upper(),
                    callback=request.callback,
                    meta=request.meta,
                )
        
        return None
```

---

## Data Validation Framework

### Comprehensive Validation System

```python
# utils/validators.py
"""
Data Validation Utilities for ResilienceAI
Comprehensive validation for scraped data
"""

import re
import json
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from urllib.parse import urlparse
import validators


class ValidationError(Exception):
    """Custom validation error."""
    pass


class FieldValidator:
    """Base class for field validators."""
    
    def __init__(self, required: bool = True, allow_empty: bool = False):
        self.required = required
        self.allow_empty = allow_empty
    
    def validate(self, value: Any, field_name: str) -> Any:
        """Validate and return cleaned value."""
        if value is None or value == '':
            if self.required and not self.allow_empty:
                raise ValidationError(f"{field_name} is required")
            return value
        
        return self._validate(value, field_name)
    
    def _validate(self, value: Any, field_name: str) -> Any:
        """Override in subclasses."""
        return value


class StringValidator(FieldValidator):
    """String field validator."""
    
    def __init__(self, min_length: int = None, max_length: int = None,
                 pattern: str = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
    
    def _validate(self, value: Any, field_name: str) -> str:
        value = str(value).strip()
        
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                f"{field_name} must be at least {self.min_length} characters"
            )
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                f"{field_name} must be at most {self.max_length} characters"
            )
        
        if self.pattern and not self.pattern.match(value):
            raise ValidationError(f"{field_name} has invalid format")
        
        return value


class URLValidator(FieldValidator):
    """URL field validator."""
    
    def __init__(self, allowed_schemes: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_schemes = allowed_schemes or ['http', 'https']
    
    def _validate(self, value: Any, field_name: str) -> str:
        value = str(value).strip()
        
        if not validators.url(value):
            raise ValidationError(f"{field_name} is not a valid URL")
        
        parsed = urlparse(value)
        
        if parsed.scheme not in self.allowed_schemes:
            raise ValidationError(
                f"{field_name} must use one of: {', '.join(self.allowed_schemes)}"
            )
        
        return value


class DateValidator(FieldValidator):
    """Date field validator."""
    
    def __init__(self, formats: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.formats = formats or [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%d %B %Y',
        ]
    
    def _validate(self, value: Any, field_name: str) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        
        value = str(value).strip()
        
        for fmt in self.formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        raise ValidationError(f"{field_name} has invalid date format")


class NumberValidator(FieldValidator):
    """Number field validator."""
    
    def __init__(self, min_value: float = None, max_value: float = None,
                 integer_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
    
    def _validate(self, value: Any, field_name: str) -> Union[int, float]:
        try:
            if self.integer_only:
                num = int(value)
            else:
                num = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a number")
        
        if self.min_value is not None and num < self.min_value:
            raise ValidationError(
                f"{field_name} must be at least {self.min_value}"
            )
        
        if self.max_value is not None and num > self.max_value:
            raise ValidationError(
                f"{field_name} must be at most {self.max_value}"
            )
        
        return num


class ListValidator(FieldValidator):
    """List field validator."""
    
    def __init__(self, item_validator: FieldValidator = None,
                 min_items: int = None, max_items: int = None, **kwargs):
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_items = min_items
        self.max_items = max_items
    
    def _validate(self, value: Any, field_name: str) -> List:
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        
        if self.min_items and len(value) < self.min_items:
            raise ValidationError(
                f"{field_name} must have at least {self.min_items} items"
            )
        
        if self.max_items and len(value) > self.max_items:
            raise ValidationError(
                f"{field_name} must have at most {self.max_items} items"
            )
        
        if self.item_validator:
            validated = []
            for i, item in enumerate(value):
                try:
                    validated.append(
                        self.item_validator.validate(item, f"{field_name}[{i}]")
                    )
                except ValidationError as e:
                    raise ValidationError(f"{field_name}[{i}]: {e}")
            return validated
        
        return value


class SchemaValidator:
    """
    Schema-based validator for complex data structures.
    """
    
    def __init__(self, schema: Dict[str, FieldValidator]):
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            
        Returns:
            Validated and cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        errors = {}
        
        # Validate defined fields
        for field_name, validator in self.schema.items():
            value = data.get(field_name)
            
            try:
                validated[field_name] = validator.validate(value, field_name)
            except ValidationError as e:
                errors[field_name] = str(e)
        
        # Check for extra fields
        extra_fields = set(data.keys()) - set(self.schema.keys())
        if extra_fields:
            # Include extra fields as-is
            for field in extra_fields:
                validated[field] = data[field]
        
        if errors:
            raise ValidationError(f"Validation failed: {errors}")
        
        return validated


# Predefined schemas
NewsItemSchema = SchemaValidator({
    'url': URLValidator(required=True),
    'title': StringValidator(min_length=5, max_length=500, required=True),
    'content': StringValidator(min_length=50, required=True),
    'source': StringValidator(min_length=2, max_length=100, required=True),
    'published_date': DateValidator(required=False),
    'scraped_date': DateValidator(required=True),
    'author': StringValidator(max_length=200, required=False),
    'tags': ListValidator(
        item_validator=StringValidator(max_length=50),
        required=False
    ),
})

DocumentItemSchema = SchemaValidator({
    'url': URLValidator(required=True),
    'title': StringValidator(min_length=5, max_length=500, required=True),
    'description': StringValidator(max_length=5000, required=True),
    'source': StringValidator(min_length=2, max_length=100, required=True),
    'metadata': FieldValidator(required=False),
    'scraped_date': DateValidator(required=True),
})


class DataQualityChecker:
    """
    Checks data quality beyond schema validation.
    """
    
    def __init__(self):
        self.quality_rules = []
    
    def add_rule(self, rule: Callable[[Dict], Optional[str]]) -> None:
        """Add a quality check rule."""
        self.quality_rules.append(rule)
    
    def check(self, data: Dict) -> Dict[str, Any]:
        """
        Run quality checks on data.
        
        Returns:
            Dictionary with quality score and issues
        """
        issues = []
        score = 100
        
        for rule in self.quality_rules:
            issue = rule(data)
            if issue:
                issues.append(issue)
                score -= 10
        
        return {
            'score': max(0, score),
            'issues': issues,
            'passed': len(issues) == 0,
        }


# Create quality checker with default rules
default_quality_checker = DataQualityChecker()

default_quality_checker.add_rule(
    lambda d: 'Content appears to be truncated' 
    if len(d.get('content', '')) < 200 else None
)

default_quality_checker.add_rule(
    lambda d: 'Title may be generic/template' 
    if d.get('title', '').lower() in ['untitled', 'home', 'index'] else None
)

default_quality_checker.add_rule(
    lambda d: 'Content has excessive repetition' 
    if len(set(d.get('content', '').split())) / max(len(d.get('content', '').split()), 1) < 0.3 
    else None
)


def validate_item(item: Dict, item_type: str = 'news') -> Dict[str, Any]:
    """
    Validate item using appropriate schema.
    
    Args:
        item: Item to validate
        item_type: Type of item ('news' or 'document')
        
    Returns:
        Validation result with status and errors
    """
    schemas = {
        'news': NewsItemSchema,
        'document': DocumentItemSchema,
    }
    
    schema = schemas.get(item_type)
    if not schema:
        return {
            'valid': False,
            'errors': {'schema': f'Unknown item type: {item_type}'},
        }
    
    try:
        validated = schema.validate(item)
        quality = default_quality_checker.check(validated)
        
        return {
            'valid': True,
            'data': validated,
            'quality': quality,
        }
    
    except ValidationError as e:
        return {
            'valid': False,
            'errors': str(e),
        }
```

---

## Scheduler Integration

### APScheduler Integration

```python
# scheduler/job_scheduler.py
"""
Job Scheduler for ResilienceAI
Manages periodic scraping jobs
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor


logger = logging.getLogger(__name__)


class ScrapingScheduler:
    """
    Scheduler for managing scraping jobs.
    
    Features:
    - Cron-based scheduling
    - Interval-based scheduling
    - Job dependency management
    - Error handling and retries
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Any] = {}
        self.running_jobs: Dict[str, Any] = {}
        
        # Scrapy settings
        self.settings = get_project_settings()
    
    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.start()
        
        # Add listeners
        self.scheduler.add_listener(
            self._on_job_executed, EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._on_job_error, EVENT_JOB_ERROR
        )
        
        logger.info("Scheduler started")
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown(wait=wait)
        logger.info("Scheduler shutdown")
    
    def schedule_spider(self,
                        spider_name: str,
                        trigger: str = 'interval',
                        **trigger_args) -> str:
        """
        Schedule a spider to run periodically.
        
        Args:
            spider_name: Name of the spider to run
            trigger: Trigger type ('cron', 'interval', 'date')
            **trigger_args: Arguments for the trigger
            
        Returns:
            Job ID
        """
        job_id = f"{spider_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create trigger
        if trigger == 'cron':
            sched_trigger = CronTrigger(**trigger_args)
        elif trigger == 'interval':
            sched_trigger = IntervalTrigger(**trigger_args)
        elif trigger == 'date':
            sched_trigger = DateTrigger(**trigger_args)
        else:
            raise ValueError(f"Unknown trigger type: {trigger}")
        
        # Add job
        job = self.scheduler.add_job(
            func=self._run_spider,
            trigger=sched_trigger,
            id=job_id,
            args=[spider_name],
            kwargs=trigger_args.get('spider_kwargs', {}),
            replace_existing=True,
        )
        
        self.jobs[job_id] = {
            'spider': spider_name,
            'trigger': trigger,
            'args': trigger_args,
        }
        
        logger.info(f"Scheduled spider {spider_name} with job ID: {job_id}")
        
        return job_id
    
    def _run_spider(self, spider_name: str, **kwargs) -> None:
        """Run a spider."""
        logger.info(f"Running spider: {spider_name}")
        
        try:
            # Create crawler process
            process = CrawlerProcess(self.settings)
            
            # Add spider
            process.crawl(spider_name, **kwargs)
            
            # Start crawling
            process.start()
            
            logger.info(f"Spider {spider_name} completed")
        
        except Exception as e:
            logger.error(f"Spider {spider_name} failed: {e}")
            raise
    
    def _on_job_executed(self, event) -> None:
        """Handle job execution completion."""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _on_job_error(self, event) -> None:
        """Handle job execution error."""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    
    def remove_job(self, job_id: str) -> None:
        """Remove a scheduled job."""
        self.scheduler.remove_job(job_id)
        del self.jobs[job_id]
        logger.info(f"Removed job: {job_id}")
    
    def pause_job(self, job_id: str) -> None:
        """Pause a scheduled job."""
        self.scheduler.pause_job(job_id)
        logger.info(f"Paused job: {job_id}")
    
    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        self.scheduler.resume_job(job_id)
        logger.info(f"Resumed job: {job_id}")
    
    def get_jobs(self) -> Dict[str, Any]:
        """Get all scheduled jobs."""
        return self.jobs
    
    def run_job_now(self, job_id: str) -> None:
        """Run a job immediately."""
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Scheduled job {job_id} to run now")


# Celery integration for distributed scheduling
from celery import Celery

celery_app = Celery('resilience_scraper')


@celery_app.task
def run_spider_task(spider_name: str, **kwargs) -> Dict[str, Any]:
    """
    Celery task to run a spider.
    
    Args:
        spider_name: Name of spider to run
        **kwargs: Spider arguments
        
    Returns:
        Task result
    """
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    # Add spider
    process.crawl(spider_name, **kwargs)
    
    # Start crawling
    process.start()
    
    return {
        'spider': spider_name,
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
    }


class DistributedScheduler:
    """
    Distributed scheduler using Celery.
    """
    
    def __init__(self):
        self.celery = celery_app
    
    def schedule_spider(self,
                        spider_name: str,
                        countdown: int = None,
                        eta: datetime = None,
                        **kwargs) -> str:
        """
        Schedule a spider task.
        
        Args:
            spider_name: Spider to run
            countdown: Seconds to wait before running
            eta: Specific time to run
            **kwargs: Spider arguments
            
        Returns:
            Task ID
        """
        task = run_spider_task.apply_async(
            args=[spider_name],
            kwargs=kwargs,
            countdown=countdown,
            eta=eta,
        )
        
        return task.id
    
    def schedule_periodic(self,
                          spider_name: str,
                          interval: timedelta,
                          **kwargs) -> None:
        """
        Schedule periodic spider runs.
        
        Args:
            spider_name: Spider to run
            interval: Run interval
            **kwargs: Spider arguments
        """
        from celery.schedules import schedule
        
        # Add periodic task
        self.celery.conf.beat_schedule = {
            f'run-{spider_name}': {
                'task': 'scheduler.job_scheduler.run_spider_task',
                'schedule': interval.total_seconds(),
                'args': [spider_name],
                'kwargs': kwargs,
            },
        }
```

---

## Legal Compliance

### Compliance Framework

```python
# utils/compliance.py
"""
Legal Compliance Utilities for ResilienceAI
Ensures ethical and legal web scraping practices
"""

import logging
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, urljoin
from datetime import datetime

import requests
from robotexclusionrulesparser import RobotExclusionRulesParser


logger = logging.getLogger(__name__)


class RobotsChecker:
    """
    Checks and respects robots.txt rules.
    """
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache: Dict[str, tuple] = {}
        self.cache_ttl = cache_ttl
        self.user_agent = 'ResilienceAI-Bot'
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if fetching is allowed
        """
        parsed = urlparse(url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", '/robots.txt')
        
        # Get or fetch robots.txt
        rp = self._get_robots_parser(robots_url)
        
        if rp:
            return rp.can_fetch(self.user_agent, url)
        
        # If no robots.txt, assume allowed
        return True
    
    def _get_robots_parser(self, robots_url: str) -> Optional[RobotExclusionRulesParser]:
        """Get cached or fetch robots.txt parser."""
        now = datetime.now().timestamp()
        
        # Check cache
        if robots_url in self.cache:
            parser, timestamp = self.cache[robots_url]
            if now - timestamp < self.cache_ttl:
                return parser
        
        # Fetch robots.txt
        try:
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                rp = RobotExclusionRulesParser()
                rp.parse(response.text)
                
                self.cache[robots_url] = (rp, now)
                return rp
        
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch robots.txt: {e}")
        
        return None
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """Get crawl-delay from robots.txt."""
        parsed = urlparse(url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", '/robots.txt')
        
        rp = self._get_robots_parser(robots_url)
        
        if rp:
            return rp.get_crawl_delay(self.user_agent)
        
        return None


class TermsOfServiceChecker:
    """
    Checks terms of service for scraping restrictions.
    """
    
    SCRAPING_KEYWORDS = [
        'scraping', 'crawler', 'bot', 'automated', 'spider',
        'data mining', 'data extraction', 'screen scraping',
    ]
    
    PROHIBITED_PATTERNS = [
        r'prohibit\w*\s+(?:any\s+)?(?:web\s+)?scraping',
        r'no\s+(?:web\s+)?scraping',
        r'forbid\w*\s+(?:any\s+)?(?:web\s+)?scraping',
        r'ban\w*\s+(?:web\s+)?scraping',
    ]
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
    
    def check_tos(self, domain: str) -> Dict[str, Any]:
        """
        Check terms of service for scraping restrictions.
        
        Args:
            domain: Domain to check
            
        Returns:
            Check result with recommendations
        """
        if domain in self.cache:
            return self.cache[domain]
        
        # Common TOS URLs
        tos_urls = [
            f"https://{domain}/terms",
            f"https://{domain}/terms-of-service",
            f"https://{domain}/tos",
            f"https://{domain}/legal/terms",
        ]
        
        result = {
            'domain': domain,
            'checked': False,
            'tos_found': False,
            'scraping_mentioned': False,
            'scraping_prohibited': False,
            'recommendation': 'proceed_with_caution',
            'notes': [],
        }
        
        for url in tos_urls:
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; ResilienceAI-Bot/1.0)'
                })
                
                if response.status_code == 200:
                    result['tos_found'] = True
                    result['checked'] = True
                    
                    text = response.text.lower()
                    
                    # Check for scraping mentions
                    for keyword in self.SCRAPING_KEYWORDS:
                        if keyword in text:
                            result['scraping_mentioned'] = True
                            result['notes'].append(f"Found keyword: {keyword}")
                    
                    # Check for prohibitions
                    for pattern in self.PROHIBITED_PATTERNS:
                        if re.search(pattern, text, re.I):
                            result['scraping_prohibited'] = True
                            result['recommendation'] = 'do_not_scrape'
                            result['notes'].append("Scraping appears to be prohibited")
                            break
                    
                    break
            
            except requests.RequestException:
                continue
        
        self.cache[domain] = result
        return result


class ComplianceManager:
    """
    Manages legal compliance for web scraping.
    """
    
    def __init__(self):
        self.robots_checker = RobotsChecker()
        self.tos_checker = TermsOfServiceChecker()
        
        # Blocked domains
        self.blocked_domains: Set[str] = set()
        
        # Respect settings
        self.respect_robots = True
        self.respect_tos = True
        self.respect_rate_limits = True
    
    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Comprehensive compliance check for URL.
        
        Args:
            url: URL to check
            
        Returns:
            Compliance check result
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        result = {
            'url': url,
            'domain': domain,
            'allowed': True,
            'checks': {},
            'warnings': [],
        }
        
        # Check blocked domains
        if domain in self.blocked_domains:
            result['allowed'] = False
            result['checks']['blocked'] = 'Domain is in blocklist'
            return result
        
        # Check robots.txt
        if self.respect_robots:
            robots_allowed = self.robots_checker.can_fetch(url)
            result['checks']['robots_txt'] = 'allowed' if robots_allowed else 'disallowed'
            
            if not robots_allowed:
                result['allowed'] = False
                result['warnings'].append('URL is disallowed by robots.txt')
        
        # Check TOS
        if self.respect_tos:
            tos_result = self.tos_checker.check_tos(domain)
            result['checks']['terms_of_service'] = tos_result
            
            if tos_result['scraping_prohibited']:
                result['allowed'] = False
                result['warnings'].append('Scraping is prohibited by terms of service')
        
        return result
    
    def block_domain(self, domain: str, reason: str = '') -> None:
        """Add domain to blocklist."""
        self.blocked_domains.add(domain.lower())
        logger.info(f"Blocked domain: {domain} - {reason}")
    
    def unblock_domain(self, domain: str) -> None:
        """Remove domain from blocklist."""
        self.blocked_domains.discard(domain.lower())
        logger.info(f"Unblocked domain: {domain}")


# Compliance middleware for Scrapy
class ComplianceMiddleware:
    """
    Scrapy middleware for legal compliance.
    """
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.compliance = ComplianceManager()
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_request(self, request, spider):
        """Check compliance before making request."""
        result = self.compliance.check_url(request.url)
        
        if not result['allowed']:
            from scrapy.exceptions import IgnoreRequest
            
            reason = '; '.join(result['warnings'])
            logger.warning(f"Blocked request to {request.url}: {reason}")
            
            raise IgnoreRequest(f"Compliance check failed: {reason}")
        
        return None
```

---

## Monitoring & Observability

### Monitoring Setup

```python
# monitoring/metrics.py
"""
Monitoring and Metrics for ResilienceAI
Tracks scraping performance and health
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server


logger = logging.getLogger(__name__)


class ScrapingMetrics:
    """
    Prometheus metrics for scraping operations.
    """
    
    def __init__(self, port: int = 8000):
        # Request metrics
        self.requests_total = Counter(
            'scraper_requests_total',
            'Total requests made',
            ['spider', 'domain', 'status']
        )
        
        self.request_duration = Histogram(
            'scraper_request_duration_seconds',
            'Request duration in seconds',
            ['spider', 'domain']
        )
        
        # Item metrics
        self.items_scraped = Counter(
            'scraper_items_scraped_total',
            'Total items scraped',
            ['spider', 'item_type']
        )
        
        self.items_dropped = Counter(
            'scraper_items_dropped_total',
            'Total items dropped',
            ['spider', 'reason']
        )
        
        # Spider metrics
        self.spider_running = Gauge(
            'scraper_spider_running',
            'Whether spider is running',
            ['spider']
        )
        
        self.spider_start_time = Gauge(
            'scraper_spider_start_time',
            'Spider start timestamp',
            ['spider']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'scraper_errors_total',
            'Total errors',
            ['spider', 'error_type']
        )
        
        # Proxy metrics
        self.proxy_requests = Counter(
            'scraper_proxy_requests_total',
            'Requests per proxy',
            ['proxy', 'status']
        )
        
        # Start metrics server
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    
    def record_request(self, spider: str, domain: str, 
                       status: int, duration: float) -> None:
        """Record request metrics."""
        status_class = f"{status // 100}xx"
        self.requests_total.labels(spider=spider, domain=domain, 
                                    status=status_class).inc()
        self.request_duration.labels(spider=spider, domain=domain).observe(duration)
    
    def record_item(self, spider: str, item_type: str) -> None:
        """Record item scraped."""
        self.items_scraped.labels(spider=spider, item_type=item_type).inc()
    
    def record_error(self, spider: str, error_type: str) -> None:
        """Record error."""
        self.errors_total.labels(spider=spider, error_type=error_type).inc()


class ScrapingMonitor:
    """
    Monitor for tracking scraping jobs and performance.
    """
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.stats_history: Dict[str, list] = defaultdict(list)
    
    def start_job(self, job_id: str, spider: str, **kwargs) -> None:
        """Record job start."""
        self.jobs[job_id] = {
            'spider': spider,
            'status': 'running',
            'start_time': datetime.now(),
            'end_time': None,
            'stats': {},
            'config': kwargs,
        }
        
        logger.info(f"Job {job_id} started")
    
    def end_job(self, job_id: str, stats: Dict = None) -> None:
        """Record job completion."""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'completed'
            self.jobs[job_id]['end_time'] = datetime.now()
            self.jobs[job_id]['stats'] = stats or {}
            
            # Add to history
            self.stats_history[self.jobs[job_id]['spider']].append({
                'job_id': job_id,
                'stats': stats,
            })
            
            logger.info(f"Job {job_id} completed")
    
    def fail_job(self, job_id: str, error: str) -> None:
        """Record job failure."""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'failed'
            self.jobs[job_id]['end_time'] = datetime.now()
            self.jobs[job_id]['error'] = error
            
            logger.error(f"Job {job_id} failed: {error}")
    
    def get_job_stats(self, job_id: str) -> Optional[Dict]:
        """Get job statistics."""
        return self.jobs.get(job_id)
    
    def get_spider_stats(self, spider: str) -> list:
        """Get historical stats for spider."""
        return self.stats_history.get(spider, [])


# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'logs/scraper.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'json_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/scraper.json',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'json_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'scrapy': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```


---

## Testing Strategy

### Test Suite Implementation

```python
# tests/test_spiders.py
"""
Test Suite for ResilienceAI Spiders
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

import pytest
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler

from resilience_scraper.spiders.news_spider import NewsSpider
from resilience_scraper.spiders.government_spider import GovernmentSpider
from resilience_scraper.items.news_item import NewsItem
from resilience_scraper.utils.parsers import BeautifulSoupParser
from resilience_scraper.utils.validators import validate_item


class TestNewsSpider(unittest.TestCase):
    """Tests for NewsSpider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.crawler = get_crawler(NewsSpider)
        self.spider = self.crawler._create_spider()
    
    def test_spider_initialization(self):
        """Test spider initializes correctly."""
        self.assertEqual(self.spider.name, 'news_spider')
        self.assertIsNotNone(self.spider.sources)
    
    def test_parse_article(self):
        """Test article parsing."""
        html = '''
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <h1>Test Headline</h1>
                    <p>First paragraph of content.</p>
                    <p>Second paragraph with more content.</p>
                </article>
            </body>
        </html>
        '''
        
        response = HtmlResponse(
            url='https://example.com/article',
            body=html.encode('utf-8'),
            meta={'source': 'test', 'title': 'Test Article'}
        )
        
        results = list(self.spider.parse_article(response))
        
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertEqual(item['url'], 'https://example.com/article')
        self.assertIn('First paragraph', item['content'])
    
    def test_url_validation(self):
        """Test URL validation."""
        valid_urls = [
            'https://example.com/article',
            'http://test.org/page',
        ]
        
        invalid_urls = [
            'ftp://example.com/file',
            'javascript:void(0)',
            'file:///etc/passwd',
        ]
        
        for url in valid_urls:
            self.assertTrue(self.spider.is_valid_url(url))
        
        for url in invalid_urls:
            self.assertFalse(self.spider.is_valid_url(url))


class TestGovernmentSpider(unittest.TestCase):
    """Tests for GovernmentSpider."""
    
    def setUp(self):
        self.crawler = get_crawler(GovernmentSpider)
        self.spider = self.crawler._create_spider()
    
    def test_api_response_parsing(self):
        """Test API response parsing."""
        api_response = {
            'result': {
                'count': 2,
                'results': [
                    {
                        'title': 'Dataset 1',
                        'url': 'https://data.gov/dataset/1',
                        'notes': 'Description 1',
                        'organization': {'title': 'Org 1'},
                        'tags': [{'name': 'tag1'}],
                    },
                    {
                        'title': 'Dataset 2',
                        'url': 'https://data.gov/dataset/2',
                        'notes': 'Description 2',
                        'organization': {'title': 'Org 2'},
                        'tags': [{'name': 'tag2'}],
                    },
                ]
            }
        }
        
        response = HtmlResponse(
            url='https://catalog.data.gov/api/3/action/package_search',
            body=json.dumps(api_response).encode('utf-8'),
            meta={'source': 'data_gov', 'params': {'start': 0, 'rows': 100}}
        )
        
        results = list(self.spider.parse_data_gov_response(response))
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Dataset 1')


class TestBeautifulSoupParser(unittest.TestCase):
    """Tests for BeautifulSoupParser."""
    
    def test_extract_text(self):
        """Test text extraction."""
        html = '''
        <html>
            <body>
                <script>alert('test');</script>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </body>
        </html>
        '''
        
        parser = BeautifulSoupParser(html)
        text = parser.extract_text()
        
        self.assertIn('First paragraph', text)
        self.assertIn('Second paragraph', text)
        self.assertNotIn('alert', text)
    
    def test_extract_article_content(self):
        """Test article content extraction."""
        html = '''
        <html>
            <head>
                <title>Article Title</title>
                <meta name="author" content="John Doe">
            </head>
            <body>
                <article>
                    <h1>Article Headline</h1>
                    <p>Article content here.</p>
                </article>
            </body>
        </html>
        '''
        
        parser = BeautifulSoupParser(html)
        content = parser.extract_article_content()
        
        self.assertEqual(content['title'], 'Article Title')
        self.assertEqual(content['author'], 'John Doe')
        self.assertIn('Article content', content['content'])
    
    def test_extract_tables(self):
        """Test table extraction."""
        html = '''
        <table>
            <caption>Test Table</caption>
            <thead>
                <tr><th>Col1</th><th>Col2</th></tr>
            </thead>
            <tbody>
                <tr><td>A</td><td>B</td></tr>
                <tr><td>C</td><td>D</td></tr>
            </tbody>
        </table>
        '''
        
        parser = BeautifulSoupParser(html)
        tables = parser.extract_tables()
        
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['caption'], 'Test Table')
        self.assertEqual(tables[0]['headers'], ['Col1', 'Col2'])
        self.assertEqual(len(tables[0]['rows']), 2)


class TestValidators(unittest.TestCase):
    """Tests for validators."""
    
    def test_news_item_validation(self):
        """Test news item validation."""
        valid_item = {
            'url': 'https://example.com/article',
            'title': 'Test Article Title',
            'content': 'This is the article content. It has enough characters.',
            'source': 'test_source',
            'scraped_date': datetime.now().isoformat(),
        }
        
        result = validate_item(valid_item, 'news')
        
        self.assertTrue(result['valid'])
        self.assertIn('data', result)
    
    def test_invalid_url(self):
        """Test invalid URL detection."""
        invalid_item = {
            'url': 'not-a-valid-url',
            'title': 'Test',
            'content': 'Content here',
            'source': 'test',
            'scraped_date': datetime.now().isoformat(),
        }
        
        result = validate_item(invalid_item, 'news')
        
        self.assertFalse(result['valid'])
    
    def test_short_content(self):
        """Test short content detection."""
        short_item = {
            'url': 'https://example.com/article',
            'title': 'Test Article',
            'content': 'Short',
            'source': 'test',
            'scraped_date': datetime.now().isoformat(),
        }
        
        result = validate_item(short_item, 'news')
        
        self.assertFalse(result['valid'])


# Integration tests
@pytest.mark.integration
class TestIntegration(unittest.TestCase):
    """Integration tests requiring external services."""
    
    @pytest.mark.skip(reason="Requires external service")
    def test_live_news_scraping(self):
        """Test live news scraping."""
        # This test would make actual HTTP requests
        pass
    
    @pytest.mark.skip(reason="Requires database")
    def test_mongodb_pipeline(self):
        """Test MongoDB pipeline."""
        pass


# Performance tests
class TestPerformance(unittest.TestCase):
    """Performance tests."""
    
    def test_parsing_speed(self):
        """Test HTML parsing speed."""
        import time
        
        # Generate large HTML
        html = '<html><body>' + '<p>Paragraph</p>' * 1000 + '</body></html>'
        
        start = time.time()
        parser = BeautifulSoupParser(html)
        text = parser.extract_text()
        elapsed = time.time() - start
        
        # Should complete in under 1 second
        self.assertLess(elapsed, 1.0)
    
    def test_validation_speed(self):
        """Test validation speed."""
        import time
        
        item = {
            'url': 'https://example.com/article',
            'title': 'Test Article',
            'content': 'Content here with enough characters for validation.',
            'source': 'test',
            'scraped_date': datetime.now().isoformat(),
        }
        
        start = time.time()
        for _ in range(100):
            validate_item(item, 'news')
        elapsed = time.time() - start
        
        # Should complete 100 validations in under 1 second
        self.assertLess(elapsed, 1.0)


# Run tests
if __name__ == '__main__':
    unittest.main()
```

### Test Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
markers =
    integration: marks tests as integration tests (may require external services)
    slow: marks tests as slow
    unit: marks tests as unit tests
```

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:5.0
        ports:
          - 27017:27017
      
      redis:
        image: redis:6
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: pytest -m unit --cov=resilience_scraper --cov-report=xml
    
    - name: Run integration tests
      run: pytest -m integration
      env:
        MONGODB_URI: mongodb://localhost:27017/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

---

## Implementation Priority

### Priority Matrix

| Component | Priority | Effort | Impact | Dependencies |
|-----------|----------|--------|--------|--------------|
| Scrapy Framework | P0 | Medium | High | None |
| BeautifulSoup Parser | P0 | Low | High | None |
| Data Validation | P0 | Medium | High | None |
| Rate Limiting | P0 | Low | High | Scrapy |
| Legal Compliance | P0 | Medium | Critical | None |
| Storage Pipeline | P1 | Medium | High | Validation |
| Headless Browsers | P1 | High | Medium | Scrapy |
| Proxy Rotation | P1 | Medium | Medium | Scrapy |
| CAPTCHA Handling | P2 | High | Low | Headless |
| Scheduler | P2 | Low | Medium | All above |
| Monitoring | P2 | Low | Medium | All above |

### Implementation Phases

#### Phase 1: Foundation (Weeks 1-2)
- [x] Scrapy framework setup
- [x] Base spider implementation
- [x] BeautifulSoup integration
- [x] Basic data validation
- [x] Rate limiting middleware
- [x] Legal compliance framework

**Deliverables:**
- Working spider for news sources
- Data validation pipeline
- robots.txt compliance
- Basic logging

#### Phase 2: Core Features (Weeks 3-4)
- [x] Government data spider
- [x] MongoDB storage pipeline
- [x] Enhanced validation schemas
- [x] Error handling and retries
- [x] Data cleaning pipeline

**Deliverables:**
- Multi-source data collection
- Persistent storage
- Quality-assured data

#### Phase 3: Advanced Features (Weeks 5-6)
- [x] Playwright integration
- [x] Proxy rotation system
- [x] CAPTCHA handling
- [x] Advanced parsing utilities
- [x] Table extraction

**Deliverables:**
- JavaScript site support
- IP rotation capability
- CAPTCHA solving

#### Phase 4: Operations (Weeks 7-8)
- [x] Job scheduler
- [x] Monitoring and metrics
- [x] Notification system
- [x] Performance optimization
- [x] Comprehensive testing

**Deliverables:**
- Automated scheduling
- Production monitoring
- Alert system

### Quick Start Implementation

```python
# quickstart.py
"""
Quick Start Script for ResilienceAI Web Scraping
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up environment for scraping."""
    # Create necessary directories
    directories = [
        'logs',
        'exports',
        'exports/news',
        'exports/government',
        'httpcache',
        'config',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Environment setup complete")

def run_news_spider():
    """Run news spider example."""
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from resilience_scraper.spiders.news_spider import NewsSpider
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    process.crawl(NewsSpider, source='reuters', max_pages=10)
    process.start()
    
    print("✓ News spider completed")

def run_government_spider():
    """Run government data spider."""
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from resilience_scraper.spiders.government_spider import GovernmentSpider
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    process.crawl(GovernmentSpider, source='fema')
    process.start()
    
    print("✓ Government spider completed")

def validate_setup():
    """Validate the scraping setup."""
    checks = [
        ('MongoDB connection', check_mongodb),
        ('Scrapy installation', check_scrapy),
        ('BeautifulSoup installation', check_bs4),
        ('Playwright installation', check_playwright),
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            check_func()
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False
    
    return all_passed

def check_mongodb():
    """Check MongoDB connection."""
    from pymongo import MongoClient
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'), 
                         serverSelectionTimeoutMS=5000)
    client.server_info()

def check_scrapy():
    """Check Scrapy installation."""
    import scrapy
    assert scrapy.__version__

def check_bs4():
    """Check BeautifulSoup installation."""
    from bs4 import BeautifulSoup
    assert BeautifulSoup

def check_playwright():
    """Check Playwright installation."""
    from playwright.sync_api import sync_playwright
    assert sync_playwright

def main():
    """Main entry point."""
    print("=" * 50)
    print("ResilienceAI Web Scraping - Quick Start")
    print("=" * 50)
    
    # Setup
    setup_environment()
    
    # Validate
    if not validate_setup():
        print("\n⚠ Some checks failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        return 1
    
    print("\n✓ All checks passed!")
    
    # Run example spiders
    print("\nRunning example spiders...")
    
    try:
        run_news_spider()
    except Exception as e:
        print(f"News spider error: {e}")
    
    try:
        run_government_spider()
    except Exception as e:
        print(f"Government spider error: {e}")
    
    print("\n✓ Quick start complete!")
    print("Check exports/ directory for results.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### Requirements Files

```txt
# requirements.txt
# Core dependencies
scrapy>=2.11.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.31.0
pydantic>=2.0.0

# Database
pymongo>=4.5.0
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.0
redis>=5.0.0

# Browser automation
playwright>=1.40.0
selenium>=4.15.0
webdriver-manager>=4.0.0

# Scheduling
APScheduler>=3.10.0
celery>=5.3.0

# Monitoring
prometheus-client>=0.18.0
python-json-logger>=2.0.0

# Utilities
python-dotenv>=1.0.0
tldextract>=5.0.0
validators>=0.22.0
robotexclusionrulesparser>=1.7.0
Pillow>=10.0.0
```

```txt
# requirements-test.txt
# Testing dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
factory-boy>=3.3.0
responses>=0.24.0
freezegun>=1.2.0
```

---

## Summary

This comprehensive web scraping architecture for ResilienceAI provides:

### Key Features Implemented

1. **Scrapy Framework**: Production-ready spider framework with base classes, middleware, and pipelines
2. **BeautifulSoup Integration**: Advanced HTML parsing with content extraction utilities
3. **Headless Browsers**: Playwright and Selenium support for JavaScript-heavy sites
4. **Data Pipelines**: Validation, cleaning, and storage to MongoDB/PostgreSQL
5. **Rate Limiting**: Adaptive rate limiting with per-domain controls
6. **Proxy Rotation**: Health-checked proxy pool with multiple rotation strategies
7. **CAPTCHA Handling**: Integration with 2captcha and Anti-Captcha services
8. **Data Validation**: Pydantic-based schema validation with quality checks
9. **Job Scheduler**: APScheduler and Celery-based distributed scheduling
10. **Legal Compliance**: robots.txt and terms of service checking
11. **Monitoring**: Prometheus metrics and comprehensive logging
12. **Testing**: Unit, integration, and performance tests

### File Structure

```
resilience_scraper/
├── config/
│   └── settings.py          # Scrapy configuration
├── spiders/
│   ├── base_spider.py       # Base spider class
│   ├── news_spider.py       # News source spider
│   └── government_spider.py # Government data spider
├── middlewares/
│   ├── proxy_middleware.py  # Proxy rotation
│   ├── rate_limit_middleware.py  # Rate limiting
│   ├── retry_middleware.py  # Retry logic
│   └── captcha_middleware.py # CAPTCHA handling
├── pipelines/
│   ├── validation_pipeline.py  # Data validation
│   ├── cleaning_pipeline.py    # Data cleaning
│   ├── storage_pipeline.py     # Data storage
│   └── notification_pipeline.py # Notifications
├── utils/
│   ├── parsers.py           # BeautifulSoup utilities
│   ├── validators.py        # Data validation
│   ├── playwright_driver.py # Browser automation
│   └── compliance.py        # Legal compliance
├── scheduler/
│   └── job_scheduler.py     # Job scheduling
├── monitoring/
│   └── metrics.py           # Monitoring setup
└── tests/
    └── test_spiders.py      # Test suite
```

### Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env` file
3. Run quick start: `python quickstart.py`
4. Customize spiders for specific data sources
5. Deploy with Docker and orchestration tools

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
