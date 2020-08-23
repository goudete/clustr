from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
import datetime
from customers.models import MenuItemCounter
from django.utils.translation import gettext as _
