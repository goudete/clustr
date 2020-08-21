from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from clustr import settings
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from .email_handlers import send_email_to_team, send_help_otw_email


def contactFormView(request):
    if request.method == "POST":
        query_dict = request.POST #request.data doesnt work for some reason

        customer_name = query_dict['name']
        email = query_dict['email']
        phone_number = query_dict['phone_number']
        website = query_dict['website']
        message = query_dict['message']

        #send email to the team to let them know about the customer's query
        send_email_to_team(request,customer_name,message,email,website,phone_number)

        #send another mail confirming help is on the way
        send_help_otw_email(email,customer_name,message)

        messages.info(request, _("Thanks ")+ " " + str(customer_name)
        + "! " + _("We have received your message and will get back to you shortly at") + " " + email)
        return HttpResponseRedirect('/restaurant_admin')
    else:
        return render(request, 'contact_form.html')
