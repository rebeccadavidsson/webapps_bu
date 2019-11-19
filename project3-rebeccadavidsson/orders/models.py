from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

MAX = 64


class Category(models.Model):
    name = models.CharField(max_length=MAX)

    def __str__(self):
        return f"{self.name}"


class Regular_pizza(models.Model):
    name = models.CharField(max_length=MAX)
    small = models.DecimalField(max_digits=4, decimal_places=2)
    large = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 3

    def __str__(self):
        return f"{self.name} - {self.small} -{self.large}"


class Sicilian_pizza(models.Model):
    name = models.CharField(max_length=MAX)
    small = models.DecimalField(max_digits=4, decimal_places=2)
    large = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 3

    def __str__(self):
        return f"{self.name} - {self.small} -{self.large}"


class Topping(models.Model):
    name = models.CharField(max_length=MAX)
    columns = 1

    def __str__(self):
        return f"{self.name}"


class Sub(models.Model):
    name = models.CharField(max_length=MAX)
    small = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    large = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 3

    def __str__(self):
        return f"{self.name} - {self.small} -{self.large}"


class Pasta(models.Model):
    name = models.CharField(max_length=MAX)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 2

    def __str__(self):
        return f"{self.name} - {self.price}"


class Salad(models.Model):
    name = models.CharField(max_length=MAX)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 2

    def __str__(self):
        return f"{self.name} - {self.price}"


class Dinner_platter(models.Model):
    name = models.CharField(max_length=MAX)
    small = models.DecimalField(max_digits=4, decimal_places=2)
    large = models.DecimalField(max_digits=4, decimal_places=2)
    columns = 3

    def __str__(self):
        return f"{self.name} - {self.small} -{self.large}"


class User_order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.IntegerField()
    topping_allowance = models.IntegerField(default=0)
    status = models.CharField(max_length=MAX, default='initiated')

    def __str__(self):
        return f"{self.user} - {self.order_number} - {self.status} Topping_allowance: {self.topping_allowance}"


class Order2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField()
    category = models.CharField(max_length=MAX, null=True)
    name = models.CharField(max_length=MAX)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price} "


class Order_counter(models.Model):
    counter = models.IntegerField()

    def __str__(self):
        return f"Order number: {self.counter}  "
