from celery import shared_task

from mysite.utils.logger import logger


@shared_task
def print_task(x):
    logger.info(f"print x : {x}")
