import razorpay
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import F
from django.shortcuts import HttpResponse, render
from razorpay import Client
from rest_framework import generics, serializers, status, views, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from .models import Cart, CartItem, Order, OrderItem, Product, User
from .serialzer import (
    CartItemAddUpdateSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
    OrderStatisticsSerializer,
    ProductSerializer,
    UserRegisterSerializer,
    UserSerializer,
)

# ------------------------------------------ ### REGISTER ### ------------------------------------------


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            data = {
                "response": "Account Has been Created Successfully",
                "username": account.username,
                "email": account.email,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class UseeRegister(views.APIView):
    
#     permission_classes = [AllowAny]
    
#     def post(self, request, *args, **kwargs):
#         serializer = UserRegisterSerializer(data = request.data)
#         if serializer.is_valid():
#             account = serializer.save()
#             data = {
#                 "message" : "User registered Successfully",
#                 "username" : account.username,
#                 "email" : account.email
#             }
#             return Response(
#                 data, status=status.HTTP_200_OK
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------ ### LOGOUT ### ------------------------------------------


@api_view(["POST"])
def logout_user(request):
    if request.method == "POST":
        print(request.user)
        request.user.auth_token.delete()
        return Response({"You have been Logged Out"}, status=status.HTTP_200_OK)


# ------------------------------------------ ### LOGIN ### ------------------------------------------

# class LoginView(views.APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         email = request.data.get("username")
#         password = request.data.get("password")
#         user = authenticate(username=email, password=password)

#         if user:
#             return Response({
#                 "message": "Login successful",
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "full_name": user.get_full_name(),
#                     "is_admin": user.is_staff
#                 }
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            # Generate the JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.get_full_name(),
                        "is_staff": user.is_staff,
                        "is_blocked" : user.is_blocked,
                        
                    },
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


# class Login(views.APIView):
#     def post(self, request, *args, **kwargs):
        
#         username = request.data.get('username')
#         password = request.data.get('password')
        
#         if not username or not password:
#             return Response({"Error": "Username and password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         user = authenticate(username=username, password = password)
#         if user:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({
#                 "message" : "success",
#                 "token" : token.key,
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({"error" : "Invalid Credentials"})

# ------------------------------------------ ### USER DETAILS FETCH ### ------------------------------------------


class UserDetailsAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "is_staff": user.is_staff,
                "username" : user.username,
            }
        )


# ------------------------------------------ ### USER DELETE ### ------------------------------------------

class DeleteUSerAPIView(views.APIView):
    permission_classes = [IsAdminUser]
    
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message" : "User Deleted Successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error" : "User Not found"}, status=status.HTTP_404_NOT_FOUND
            )

# ------------------------------------------ ### USER BLOCK UNLOCK ### ------------------------------------------


class BlockUnblockUserView(views.APIView):
    permission_classes = [IsAdminUser] 

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get("action", "").lower()
        if action == "block":
            user.is_blocked = True
            user.save()
            return Response(
                {"message": f"User {user.username} has been blocked."},
                status=status.HTTP_200_OK,
            )
        elif action == "unblock":
            user.is_blocked = False
            user.save()
            return Response(
                {"message": f"User {user.username} has been unblocked."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid action. Use 'block' or 'unblock'."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ------------------------------------------ ### PRODUCT ### ------------------------------------------


# class ProductListCreateAPIView(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     # pagination_class = ProductPagination
#     filter_backends = [SearchFilter]
#     search_fields = ["name", "description"]

#     def get_permissions(self):
#         if self.action in ["list", "retrieve"]:
#             permission_classes = [AllowAny]
#         else:
#             permission_classes = [IsAdminUser]
#         return [permission() for permission in permission_classes]
from .utils.s3_utils import upload_image_to_s3
class ProductListCreateAPIView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]



class ProductsByCategoryAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, category, *args, **kwargs):
        valid_categories = dict(Product.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            return Response(
                f"{category} is not avilable, available categories are {', '.join(valid_categories)}"
            )
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------------ ### CART ### ------------------------------------------


class CartListAPIView(generics.ListAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        # user = self.request.user
        # query = super().get_queryset()
        # return query.filter(user=user)
        user = self.request.user
        query = Cart.objects.select_related('user').prefetch_related('cartItems__product')
        return query.filter(user=user)
        


class CartAddAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemAddUpdateSerializer

    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data["product"]
            quantity = serializer.validated_data["quantity"]
            size = serializer.validated_data["size"]

            if product.stock < quantity:
                return Response(
                    {"error": "Insufficient Stock"}, status=status.HTTP_400_BAD_REQUEST
                )

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, size=size
            )
            if created:
                cart_item.size = size
                cart_item.quantity = quantity
            else:
                cart_item.size = size
                cart_item.quantity += quantity

            cart_item.save()
            return Response(
                CartItemSerializer(cart_item).data, status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemDeleteAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            # cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart__user=request.user, pk=pk)

            cart_item.delete()
            return Response(
                {"message": "Item Deleted Successfully"}, status=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart Not Existing"}, status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not existing"}, status=status.HTTP_404_NOT_FOUND
            )


class CartItemIncreaseQuantityAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, pk=pk)
            if cart_item.product.stock < cart_item.quantity + 1:
                raise ValidationError({"error": "Insufficient Stock"})

            cart_item.quantity += 1
            cart_item.save()
            return Response(
                {"message": "Quantity Increased Successfully"},
                status=status.HTTP_200_OK,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CartItemDecreaseQuantityAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, pk=pk)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return Response(
                    {"message": "Item quantity decreased successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                cart_item.delete()
                return Response(
                    {"message": "Item Deleted Successfully"}, status=status.HTTP_200_OK
                )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


class TotalCartListAPIView(views.APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        cartItems = Cart.objects.all()
        serializer = CartSerializer(cartItems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------------ ### CHECKOUT ### ------------------------------------------


class CheckoutAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            cart_items = serializer.validated_data["cart_items"]
            address = serializer.validated_data["address"]

            order_data = {
                "user": request.user,
                "address": address,
                "status": Order.StatusChoices.PENDING,
            }

            try:
                with transaction.atomic():
                    order = Order.objects.create(**order_data)
                    total_amount = 0
                    order_items = []
                    product_update = []
                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity = cart_item.quantity

                        if product.stock < quantity:
                            raise serializers.ValidationError(
                                f"Insufficient Stock for {product.name}",
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        
                        order_items.append(
                            OrderItem(
                               order=order, product=product, quantity=quantity 
                            )
                        )
                        
                        product.stock = F("stock") - quantity
                        product_update.append(product)
                        total_amount += product.price * quantity
                        
                        
                        # OrderItem.objects.create(
                        #     order=order, product=product, quantity=quantity
                        # )

                        # product.stock -= quantity
                        # product.save()

                    OrderItem.objects.bulk_create(order_items)
                    Product.objects.bulk_update(product_update, ["stock"])
                    
                    cart_items.delete()

                    # Razorpay integration
                    client = Client(
                        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                    )
                    razorpay_order = client.order.create(
                        {
                            "amount": int(total_amount * 100),  # Total amount in paise
                            "currency": "INR",
                            "receipt": str(order.order_id),
                            "payment_capture": 1,
                        }
                    )

                    order.payment_id = razorpay_order["id"]
                    order.save()

                    return Response(
                        {
                            "razorpay_order": razorpay_order,
                            "order_details": OrderSerializer(order).data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# ------------------------------------------ ### ORDER ### ------------------------------------------


class UserOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user
        query = super().get_queryset()
        return query.filter(user=user)


class OrderListAPIView(views.APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOrderCancelAPIView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, pk=pk)
            order.status = order.StatusChoices.CANCELLED
            order.save()
            return Response(
                {"message": "Order Cancelled Successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        except Order.DoesNotExist:
            return Response(
                {"message": "Order Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


class OrderStatisticsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        total_orders = Order.objects.count()
        total_earnings = 0
        total_earnings = sum(
            OrderSerializer(order).data["total_price"] for order in Order.objects.all()
        )
        return Response(
            {"total_orders": total_orders, "total_earnings": total_earnings}
        )


# ------------------------------------------ ### USER ### ------------------------------------------


class UserListAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
