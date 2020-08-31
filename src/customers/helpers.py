from cashier.models import CashierProfile
from restaurant_admin.models import ShippingZone

def assignToCashier(cart,restaurant):
    #choose cashier handling least amount of orders
    cashier = CashierProfile.objects.filter(restaurant=restaurant).filter(is_active=True).order_by('number_of_carts').first()
    cart.cashier = cashier
    cashier.number_of_carts += 1
    cashier.save()
    cart.save()

def calculate_shipping(cart):
    customer_place_id = cart.shipping_info.city_id
    restaurant_zones = ShippingZone.objects.filter(restaurant = cart.restaurant)
    for zone in restaurant_zones:
        if str(customer_place_id) == str(zone.place_id):
            return zone.cost
    return cart.restaurant.default_shipping_cost
