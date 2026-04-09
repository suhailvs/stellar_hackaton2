from celery import shared_task
from .views import stream_payments_fun
@shared_task
def stream_payments_watcher():
    stream_payments_fun()