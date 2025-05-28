from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from email.mime.image import MIMEImage

def send_application_accepted(to_email, context):
    subject = "Сіздің өтініміңіз қабылданды"
    from_email = "ppi@orleu-edu.kz"

    html_content = render_to_string("emails/application_accepted.html", context)

    email = EmailMultiAlternatives(subject, "", from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_application_updated(to_email, context):
    subject = "Сіздің өтініміңіз жаңартылды"
    from_email = "ppi@orleu-edu.kz"

    html_content = render_to_string("emails/application_updated.html", context)

    email = EmailMultiAlternatives(subject, "", from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
