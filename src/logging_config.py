import logging

def setup_logging(level=logging.INFO, format_string=None):
    """
    Central logging configuration for the entire application.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom log format (default: standard format)
    """
    if format_string is None:
        format_string = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

    logging.basicConfig(
        level=level,
        format=format_string
    )

def get_logger(name):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

