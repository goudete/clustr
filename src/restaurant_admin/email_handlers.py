from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
import datetime
from customers.models import MenuItemCounter

def send_order_email(from_email,to,order):
    subject = "ORDER #" + str(order.id)
    item_counters = MenuItemCounter.objects.filter(cart = order).all()
    msg = EmailMultiAlternatives(subject, "Hi", from_email, [to])
    current_date = datetime.date.today()
    html_template = get_template("restaurant/emails/order_info/order_info2_EN.html").render({
                                                'date':current_date,
                                                'receipt_number':order.id,
                                                'path':order.restaurant.photo_path,
                                                'order_id':order.id,
                                                'item_counters': item_counters,
                                                'cart': order
                                    })
    msg.attach_alternative(html_template, "text/html")
    msg.send()
