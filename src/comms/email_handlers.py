from django.template.loader import get_template
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import gettext as _
from clustr import settings
from django.http import HttpResponse, HttpResponseRedirect


def send_help_otw_email(email,customer_name,message):
    subject, from_email, to = _('Help is on the way!'), settings.EMAIL_HOST_USER, email
    text_content = render_to_string('emails/help_otw/help_otw_ES_txt.html', {
    'name': customer_name,
    'message':message
    })
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    html_template = get_template("emails/help_otw/help_otw_ES.html").render({
                                'name': customer_name,
                                'message':message
                                })
    msg.attach_alternative(html_template, "text/html")
    msg.send()

def send_email_to_team(request,customer_name,message,email,website,phone_number):
    if request.user.is_authenticated: #if user is logged in
        out_message = "Hi, " + customer_name + " has contacted the team with the following message: \n \n"
        out_message += message + "\n \n"
        out_message += "Get back to him at " + email + ". \n \n \n"

        user = request.user
        out_message += "Additional user info:  \n \n"
        out_message += "username: " + str(user.username) + "\n"
        out_message += "registered email: " + str(user.email) + "\n"
        if len(website) > 0:
            out_message += "given website: " + website + "\n"
        if len(phone_number) > 0:
            out_message += "given phone number: " + phone_number + "\n"
        send_mail(
        customer_name + ' HAS A NEW HELP REQUEST!', #email subject
        out_message, #email content
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently = False,
        )
        return HttpResponseRedirect('/restaurant_admin')
    else:
        out_message = """Hi, an unauthenticated user named """ + customer_name
        out_message += """ has contacted the team with the following message: \n \n """
        out_message += message + "\n \n"
        out_message += "Get back to him at " + email + ". \n \n \n"
        if len(website) > 0:
            out_message += "given website: " + website + "\n"
        if len(phone_number) > 0:
            out_message += "given phone number: " + phone_number + "\n"
        send_mail(
        customer_name + ' HAS A NEW HELP REQUEST!', #email subject
        out_message, #email content
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently = False,
        )
