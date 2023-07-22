import logging



def trace(func):
    logger = logging.getLogger(func.__name__)
    async def wrapper(*args, **kwargs):
        logger.info(f"status=start")
        result = await func(*args, **kwargs)
        logger.info(f"status=finish result={result}")

    return wrapper