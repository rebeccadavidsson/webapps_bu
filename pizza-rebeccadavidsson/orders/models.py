from django.db import models
from django.contrib.auth.models import User


class Topping(models.Model):
    toppingname = models.CharField(max_length=64)
    possible = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.toppingname}'


class Pizza(models.Model):
    """docstring for Pizza."""
    category = models.CharField(max_length=10)
    name = models.CharField(max_length=64)
    large_price = models.DecimalField(max_digits=5, decimal_places=2)
    small_price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):

        if self.large_price and self.small_price:
            return f'{self.name}, {self.small_price}, {self.large_price}'
        elif self.large_price:
            return f'{self.name}, {self.large_price}'
        elif self.small_price:
            return f'{self.name}, {self.small_price}'


class Salad(models.Model):
    category = models.CharField(max_length=10)
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.name}, {self.price}'


class Item(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, null=True, blank=True)
    salad = models.ForeignKey(Salad, on_delete=models.CASCADE, null=True, blank=True)

    # One pizza can have several toppings
    toppings = models.ManyToManyField(Topping, related_name="toppings")
    # price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'Pizza: {self.pizza}, salad: {self.salad}, topping: {self.toppings.all()}'


class Order(models.Model):

    # Every order is specific to the currently logged in user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # One order can have several items
    item = models.ManyToManyField(Item)

    def __str__(self):
        return f'{self.item}'
