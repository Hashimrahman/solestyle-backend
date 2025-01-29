from django.conf import settings
from razorpay import Client
from rest_framework import serializers
from .utils.s3_utils import upload_image_to_s3

from .models import Cart, CartItem, Order, OrderItem, Product, User


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "mobile_number",
            "password",
            "password2",
        ]

    def save(self):
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"Error": "Password Does Not Match"})

        if User.objects.filter(email=self.validated_data["email"]).exists():
            raise serializers.ValidationError({"email": ["Email Already Existing"]})

        if User.objects.filter(
            mobile_number=self.validated_data["mobile_number"]
        ).exists():
            raise serializers.ValidationError(
                {"mobile_number": ["Mobile Number Already Existing"]}
            )
        if User.objects.filter(username=self.validated_data["username"]).exists():
            raise serializers.ValidationError(
                {"username": ["Username is not available"]}
            )
        # def validate_email(self, value):
        #     if User.objects.filter(email=value).exists():
        #         raise serializers.ValidationError(
        #             "This email is already registered."
        #         )
        #     return value

        # def validate_mobile_number(self, value):
        #     if User.objects.filter(mobile_number=value).exists():
        #         raise serializers.ValidationError(
        #             "This mobile number is already registered."
        #         )
        #     return value

        # def validate_username(self, value):
        #     if User.objects.filter(username=value).exists():
        #         raise serializers.ValidationError(
        #             "This username is already taken."
        #         )
        #     return value

        account = User(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            mobile_number=self.validated_data["mobile_number"],
        )
        account.set_password(password)
        account.save()

        return account


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ------------------------------------------ ### PRODUCT ### ------------------------------------------


# class ProductSerializer(serializers.ModelSerializer):

#     image_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = "__all__"

#         def validate_price(self, value):
#             if value <= 0:
#                 raise serializers.ValidationError("Price Must be greater than zero")
#             return value


#     def get_image_url(self, obj):
#         if obj.image:
#             return obj.image.url
#         return None
class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
        
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            print("Serialized Image URL:", url)
            return url
        return None


    def create(self, validated_data):
        image_file = validated_data.get('image')
    
        if image_file:
            image_name = f'products/{image_file.name}'  # 'products/' is the folder where you want to store images in S3
            image_url = upload_image_to_s3(image_file, image_name)
            print("ser url", image_url)
            if not image_url:
                raise serializers.ValidationError("Image upload failed.")
            validated_data['image'] = image_url
            print("Final Image Data Saved:", validated_data['image'])
        return super().create(validated_data)



# ------------------------------------------ ### CART ### ------------------------------------------


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="product.price"
    )
    product_image = serializers.ImageField(source="product.image")
    product_stock = serializers.IntegerField(source="product.stock")

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_name",
            "product_price",
            "product_image",
            "product_stock",
            "quantity",
            "item_subtotal",
            "size",
        ]


class CartSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    cartItems = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField(method_name="total")

    def total(self, obj):
        cart_items = obj.cartItems.all()
        return sum(item.item_subtotal for item in cart_items)

    class Meta:
        model = Cart
        fields = ["user", "username", "cartItems", "total_price"]


class CartItemAddUpdateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    size = serializers.CharField()

    class Meta:
        model = CartItem
        fields = ["product", "quantity", "size"]

    def validate(self, data):
        product = data["product"]
        size = data["size"]
        sizes = product.sizes

        if int(size) not in sizes:
            raise serializers.ValidationError(
                {"size": "Selected size is not available !!"}
            )
        return data


# ------------------------------------------ ### CHECK OUT ### ------------------------------------------


# class CheckoutSerializer(serializers.Serializer):
#     address = serializers.CharField(max_length=255)

#     def validate(self, data):
#         cart, _ = Cart.objects.get_or_create(user=self.context["request"].user)
#         cart_items = CartItem.objects.filter(cart=cart)

#         if not cart_items:
#             raise serializers.ValidationError("Your Cart is Empty")
#         data["cart_items"] = cart_items
#         return data
# class CheckoutSerializer(serializers.Serializer):
#     street_address = serializers.CharField(max_length=255)
#     pincode = serializers.CharField(max_length=6)
#     city = serializers.CharField(max_length=100)
#     state = serializers.CharField(max_length=100)
#     country = serializers.CharField(max_length=100)

#     def validate(self, data):
#         cart, _ = Cart.objects.get_or_create(user=self.context["request"].user)
#         cart_items = CartItem.objects.filter(cart=cart)


#         if not cart_items:
#             raise serializers.ValidationError("Your Cart is Empty")
#         data["cart_items"] = cart_items
#         return data
class CheckoutSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    street_address = serializers.CharField(max_length=255)
    pincode = serializers.CharField(max_length=6)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)

    def validate(self, data):
        cart, _ = Cart.objects.get_or_create(user=self.context["request"].user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            raise serializers.ValidationError("Your Cart is Empty")

        data["address"] = {
            "phone": data["phone"],
            "street_address": data["street_address"],
            "pincode": data["pincode"],
            "city": data["city"],
            "state": data["state"],
            "country": data["country"],
        }

        data["cart_items"] = cart_items
        return data


# ------------------------------------------ ### ORDER ### ------------------------------------------


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_category = serializers.CharField(source="product.category")
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="product.price"
    )
    product_image = serializers.ImageField(source="product.image")

    class Meta:
        model = OrderItem
        fields = [
            "product_name",
            "product_price",
            "product_category",
            "product_image",
            "quantity",
            "item_subtotal",
            "is_cancelled",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="total")
    razorpay_order = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username")

    def total(self, obj):
        order_items = obj.items.all()
        return sum(item.item_subtotal for item in order_items)

    class Meta:
        model = Order
        fields = [
            "user",
            "username",
            "order_id",
            "created_at",
            "address",
            "status",
            "items",
            "total_price",
            "razorpay_order",
        ]

    def get_razorpay_order(self, obj):
        if not obj.payment_id:
            return None
        try:
            client = Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            razorpay_order = client.order.fetch(obj.payment_id)
            return razorpay_order
        except Exception as e:
            return {"error": str(e)}


class OrderStatisticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        total_orders = Order.objects.count()
        total_earnings = sum(
            OrderSerializer(order).data["total_price"] for order in Order.objects.all()
        )

        return {"total_orders": total_orders, "total_earnings": total_earnings}
