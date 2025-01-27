import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


# ------------------------------------------ ### USER ### ------------------------------------------

class User(AbstractUser):
    mobile_number = models.CharField(max_length=15, unique=True)
    is_blocked = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, default="default_username")

    # Specify custom related_name to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Custom related_name
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Custom related_name
        blank=True,
    )

    def __str__(self):
        return self.username

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ------------------------------------------ ### PRODUCT ### ------------------------------------------

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)  # Dropdown for category
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    sizes = models.JSONField()
    brand = models.CharField(max_length=100)
    stock = models.IntegerField()
    trending = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Image field
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return self.name

# ------------------------------------------ ### CART ### ------------------------------------------  

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartItems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(0),MaxValueValidator(100)]
    )
    size = models.CharField(max_length=10) 
    
    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size}) in cart of {self.cart.user.username}"

# ------------------------------------------ ### ORDER ### ------------------------------------------

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending",
        COMPLETED = "completed",
        CANCELLED = "cancelled"
    
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    products = models.ManyToManyField(Product, through="OrderItem", related_name="orders")
    address = models.JSONField(default=dict)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    is_cancelled = models.BooleanField(default=False)
    
    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.order_id}"
    
    
    
    
    