from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    path("login/", obtain_auth_token, name="login"),
    path("login-form/", views.LoginView.as_view(), name="login-form"),
    path("logout/", views.logout_user, name="logout"),
    # path("products/", views.ProductListCreateAPIView.as_view(), name="logout"),
    path("user-details/", views.UserDetailsAPIView.as_view(), name="user-deatail"),
    path("user/block-unblock/<int:user_id>/", views.BlockUnblockUserView.as_view(), name="block-unblock-user"),
    path('delete-user/<int:user_id>/', views.DeleteUSerAPIView.as_view(), name='delete-user'),  
    # path('product-delete-update/<int:product_id>/',views.ProductDeleteUpdateAPIView.as_view(), name='product-details'),
    path(
        "products/category/<str:category>/",
        views.ProductsByCategoryAPIView.as_view(),
        name="products-by-category",
    ),
    path("cart/", views.CartListAPIView.as_view(), name="cart"),
    path("total-cart/", views.TotalCartListAPIView.as_view(), name="total-cart"),
    path("cart/add/", views.CartAddAPIView.as_view(), name="cart"),
    path(
        "cart/items/<int:pk>/increase/",
        views.CartItemIncreaseQuantityAPIView.as_view(),
        name="cart-item-increase",
    ),
    path(
        "cart/items/<int:pk>/decrease/",
        views.CartItemDecreaseQuantityAPIView.as_view(),
        name="cart-item-decrease",
    ),
    path(
        "cart/items/<int:pk>/delete/",
        views.CartItemDeleteAPIView.as_view(),
        name="cart-item-delete",
    ),
    path("checkout/", views.CheckoutAPIView.as_view(), name="checkout"),
    # path('payment-verify/', views.verify_payment, name='verify-payment'),
    path("order/", views.UserOrderListAPIView.as_view(), name="order-list"),
    path(
        "order/<str:pk>/cancel/",
        views.UserOrderCancelAPIView.as_view(),
        name="order-cancel",
    ),
    path(
        "order-statistics/",
        views.OrderStatisticsView.as_view(),
        name="order-statistics",
    ),
    path(
        "total-orders/",
        views.OrderListAPIView.as_view(),
        name="total-orders",
    ),
]


router = DefaultRouter()
router.register("products", views.ProductListCreateAPIView, basename="products")
router.register("users", views.UserListAPIView, basename="user")

urlpatterns += router.urls
