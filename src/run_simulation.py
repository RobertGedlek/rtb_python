import logging
from concurrent.futures import ThreadPoolExecutor
from src.publisher.config import PublisherConfig
from src.publisher.engine import Publisher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

def start_publishers():
    configs = [
        PublisherConfig("TechBlog", "tech-world.com", "technology", 1.5, 4.0),
        PublisherConfig("SportPortal", "fast-sports.pl", "sports", 0.5, 1.2),
        PublisherConfig("NewsSite", "daily-news.com", "news", 0.1, 0.8),
    ]


    with ThreadPoolExecutor(max_workers=len(configs)) as executor:
        for cfg in configs:
            pub = Publisher(cfg)
            executor.submit(pub.run_simulation, 2.0)


if __name__ == "__main__":
    start_publishers()