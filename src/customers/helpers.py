from cashier.models import CashierProfile

def assignToCashier(cart,restaurant):
    #choose cashier handling least amount of orders
    cashier = CashierProfile.objects.filter(restaurant=restaurant).filter(is_active=True).order_by('number_of_carts').first()
    cart.cashier = cashier
    cashier.number_of_carts += 1
    cashier.save()
    cart.save()
