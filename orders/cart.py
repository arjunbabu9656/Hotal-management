from decimal import Decimal
from django.conf import settings
from menu.models import FoodItem

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, food_item, quantity=1, instructions="", override_quantity=False):
        item_id = str(food_item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {
                'quantity': 0,
                'price': str(food_item.price),
                'instructions': instructions
            }
        
        if override_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        
        self.cart[item_id]['instructions'] = instructions
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, food_item):
        item_id = str(food_item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def __iter__(self):
        item_ids = self.cart.keys()
        food_items = FoodItem.objects.filter(id__in=item_ids)
        cart = self.cart.copy()
        
        for item in food_items:
            cart[str(item.id)]['food_item'] = item

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
