from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings

def send_email_purchase(subject, email_to, data_ctx):
    ctx = data_ctx
    message = get_template('email_purchase_status.template.html').render(ctx)
    msg = EmailMessage(
        subject,
        message,
        None,
        [email_to],
    )
    msg.content_subtype = "html" 
    return msg.send()