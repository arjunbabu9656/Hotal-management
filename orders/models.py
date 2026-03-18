from django.db import models
from django.contrib.auth.models import User
from menu.models import FoodItem

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivering', 'On the Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    ORDER_TYPE_CHOICES = (
        ('delivery', 'Room Delivery'),
        ('pickup', 'Restaurant Pickup'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash on Delivery'),
        ('card', 'Card Payment'),
        ('upi', 'UPI Payment'),
    )
    is_internal = models.BooleanField(default=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    room_number = models.CharField(max_length=10, blank=True, null=True)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='delivery')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_note = models.TextField(blank=True, null=True)
    
    # Feedback & Rating
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    
    # Archiving for Daily Reset
    is_archived = models.BooleanField(default=False)
    
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_processed')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    instructions = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} (Order #{self.order.id})"
class OrderMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_staff_message = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender.username} on Order #{self.order.id}"
