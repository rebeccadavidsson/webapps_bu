from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core import serializers
import json
from .models import Pizza, Salad, Topping, Order, Item


def index(request):
    """ Load menu """
    print(Order.objects.filter(user=request.user), "KSDHFK")
    if not Order.objects.filter(user=request.user):
        orders, prices, toppings = None, None, None
    else:
        pizzas, prices, ids, toppings = get_price_and_pizzas(request)
        orders = zip(pizzas, prices, ids, toppings)
        prices = round(sum(prices), 2)

    context = {
        "pizzas": Pizza.objects.filter(category="pizza"),
        "salads": Pizza.objects.filter(category="salad"),
        "toppings": Topping.objects.all(),
        "orders": orders,
        "total": prices,
        "toppings_chosen": toppings,
    }

    return render(request, "index.html", context)


def get_price_and_pizzas(request):
    """ Calculate total price and get ordered pizza's """

    orders = Order.objects.filter(user=request.user).values('item').values_list("item", flat=True)
    tt, pizzanames, itemslist_temp, itemslist, prices, items, ids = [], [], [], [], [], [], []
    [itemslist.append(order) for order in orders]
    [itemslist_temp.append(Item.objects.filter(id=item)) for item in itemslist]
    [items.append(item.first()) for item in itemslist_temp]

    # Calculate total price from all individual orders of a user
    for item in items:
        tt.append(item.toppings.strip("[]").strip("'"))
        prices.append(float(item.price))
        pizzanames.append(item.pizza)
        ids.append(item.id)

    # Return all ordered pizza's and total price
    return pizzanames, prices, ids, tt


def add_topping(request):
    """
    Add topping to pizza on click of 'Save Toppings' button
    Directly create item and add it to Order, sepcific to current user.
    """

    # Index into list values
    for el in request.GET: value = el
    ids = value.split(",")

    # Get item name and pop from id-list
    name = ids[0]
    ids.pop(0)
    price = ids[0]
    ids.pop(0)

    # Convert strings to integers to get id's
    nums, tops, toppings = [], [], []
    [nums.append(int(num)) for num in ids]
    [tops.append(Topping.objects.filter(id=i).values('toppingname').first().values()) for i in nums]
    [toppings.append(list(i)[0]) for i in tops]

    # Get pizza object with pizza-name
    pizza = Pizza.objects.filter(name=name).first()

    # Make new item with these toppings
    item = Item(pizza=pizza, price=price, toppings=toppings)
    item.save()

    # Check if this user already has an order
    order = Order.objects.filter(user=request.user).first()

    # Create new order for this user if it doesn't exist
    if order is None:
        order = Order(user=request.user)
        order.save()

    # Add item to orders for this user
    order.item.add(item)
    order.save()

    return HttpResponse("Redirect index")


def delete(request, order):
    """ Get selected item and delete from orders """
    Item.objects.filter(id=order).delete()

    return redirect("/")
