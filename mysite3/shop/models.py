from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Tовары относятся к разным категориям.
class Category(models.Model):
    name = models.CharField(unique=True, max_length=200)

    def __str__(self):
        return self.name


class Category_photo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='category')

    def __str__(self):
        return self.photo.name


# Поставщики: python manage.py runserver
class Provider(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=24)  #  IntegerField(default=0)
    email = models.EmailField(null=True)
    address = models.CharField(max_length=400, default='')

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=200, unique=True, default='')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True) # model
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    description = models.CharField(max_length=4000, default='')
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(null=False)
    production_date = models.DateField(blank=True, null=True)#(default=timezone.now) # incoming
    providers = models.ManyToManyField(Provider)
    reserved = models.IntegerField(default=0)

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


class Guest(User):
    is_superuser = False
    is_staff = False

    def __str__(self):
        return self.username


class Product_in_cart(models.Model):
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.CharField(max_length=4000, default='')

    def __str__(self):
        return self.content


class Order(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT)
    date = models.DateTimeField(default=timezone.now)
    coming_date = models.DateField(blank=True, null=True)
    payed = models.BooleanField(default=False)
    received  = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Ordered_product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name

# class Payment_requisites(models.Model):
