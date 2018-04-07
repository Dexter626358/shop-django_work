from django.contrib import admin

from .models import Category_photo, Product, Provider, Category, Guest, Product_in_cart, Photo, Mini_photo

admin.site.register(Product)
admin.site.register(Provider)
admin.site.register(Category)
admin.site.register(Guest)
admin.site.register(Product_in_cart)
admin.site.register(Photo)
admin.site.register(Mini_photo)
admin.site.register(Category_photo)