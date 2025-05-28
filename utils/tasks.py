from celery import shared_task
from utils.email import send_application_accepted, send_application_updated


@shared_task
def send_application_accepted_task(to_email, full_name):
    context = {"full_name": full_name}
    send_application_accepted(to_email, context)


@shared_task
def send_application_updated_task(to_email, full_name):
    context = {"full_name": full_name}
    send_application_updated(to_email, context)
