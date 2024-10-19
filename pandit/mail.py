from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(to_email, subject, body):
    """
    Sends an email with dynamic to, subject, and body.
    Email body starts with 'Mail from panditplus.in:'.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    final_body = f"Mail from panditplus.in:\n\n{body}"  # Prepend the custom message
    
    # Use send_mail to send the email
    send_mail(subject, final_body, from_email, [to_email], fail_silently=False)
