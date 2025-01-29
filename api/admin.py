from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product,Order,OrderItem

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'full_name', 'mobile_number', 'is_blocked', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'mobile_number')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'mobile_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('is_blocked',)}),
    )
    
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'mobile_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('is_blocked',)}),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'trending', 'get_sizes','image')  # Added get_sizes to display sizes
    list_filter = ('category', 'trending')  # Filter options on the sidebar
    search_fields = ('name', 'category', 'brand')  # Search fields
    list_editable = ('price', 'stock', 'trending')  # Fields that can be edited directly in the list view
    # ordering = ('-price',)  # Default ordering by price

    def get_sizes(self, obj):
        return ", ".join(map(str, obj.sizes))  # Display sizes as a comma-separated string
    get_sizes.short_description = 'Sizes'  # Set the column title in the admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]



admin.site.register(User, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)

