from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from qr import settings
from django.template.loader import get_template
from django.template.loader import render_to_string

def contactFormView(request):
    if request.method == "POST":
        query_dict = request.POST #request.data doesnt work for some reason

        customer_name = query_dict['name']
        email = query_dict['email']
        phone_number = query_dict['phone_number']
        website = query_dict['website']
        message = query_dict['message']

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

            #send another mail confirming help is on the way
#             send_mail(
#             'Help is on the way!', #email subject
#             """Dear """ + customer_name + """, \n
# Thank you for reaching out to the Shift team! \n
# We will review your message and get back to you soon. \n \n
# Never alone with Shift! \n
# Your Shift team \n \n
# Here your request: \n""" + message, #email content
#             settings.EMAIL_HOST_USER,
#             [email],
#             fail_silently = False,
#             )

            subject, from_email, to = 'La ayuda va en camino', settings.EMAIL_HOST_USER, email
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

            messages.info(request, "Thanks "+ str(customer_name)
            + "! We have received your message and will get back to you shortly at " + email)
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

            #send another mail confirming help is on the way
#             send_mail(
#             'Help is on the way!', #email subject
#             """Dear """ + customer_name + """, \n
# Thank you for reaching out to the Shift team! \n
# We will review your message and get back to you soon. \n \n
# Never alone with Shift! \n
# Your Shift team \n \n
# Here your request: \n""" + message, #email content
#             settings.EMAIL_HOST_USER,
#             [email],
#             fail_silently = False,
#            )

            subject, from_email, to = 'La ayuda va en camino', settings.EMAIL_HOST_USER, email
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

            messages.info(request, "Thanks "+ str(customer_name)
            + "! We have received your message and will get back to you shortly at " + email)
            return HttpResponseRedirect('/restaurant_admin')
    else:
        return render(request, 'contact_form.html')
