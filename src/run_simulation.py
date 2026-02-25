from concurrent.futures import ThreadPoolExecutor
from src.logging_config import setup_logging
from src.publisher.config import PublisherConfig
from src.publisher.engine import Publisher

# Initialize central logging configuration
setup_logging()

def start_publishers():
    # Define multiple publisher configurations
    configs = [
        PublisherConfig("TechBlog", "tech-world.com", "technology", 1.5, 4.0),
        PublisherConfig("SportPortal", "fast-sports.pl", "sports", 0.5, 1.2),
        PublisherConfig("NewsSite", "daily-news.com", "news", 0.1, 0.8),
    ]

    # Run all publishers in parallel threads
    with ThreadPoolExecutor(max_workers=len(configs)) as executor:
        for cfg in configs:
            pub = Publisher(cfg)
            executor.submit(pub.run_simulation, 2.0)


if __name__ == "__main__":
    start_publishers()