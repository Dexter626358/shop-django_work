from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Tовары относятся к разным категориям.
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Category_photo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='category')

    def __str__(self):
        return self.photo.name


# Поставщики:
class Provider(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=24)  #  IntegerField(default=0)
    email = models.EmailField(null=True,)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=4000, default='')
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    incoming_date = models.DateTimeField(default=timezone.now)
    providers = models.ManyToManyField(Provider)

    def __str__(self):
        return self.name


class Photo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos') # shop/static/shop/photos

    def __str__(self):
        return self.photo.name


class Mini_photo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mini = models.ImageField(upload_to='mini_photos')

    def __str__(self):
        return self.mini.name


class Product_in_cart(models.Model):
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product.name

class Guest(User):
    products_cart = models.ManyToManyField(Product_in_cart)
    is_superuser = False
    is_staff = False

    def __str__(self):
        return self.username