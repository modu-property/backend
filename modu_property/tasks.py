from celery import shared_task

from app.services.collect_property_news import CollectPropertyNewsService


@shared_task
def collect_property_news_task(display: int):
    service = CollectPropertyNewsService(display=display)
    service.execute()
