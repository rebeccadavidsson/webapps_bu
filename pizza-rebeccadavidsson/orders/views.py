from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core import serializers
import json

from .models import Pizza, Salad, Topping, Order, Item


def index(request):
    """ Load menu """

    print("IK LAAD HET MENU")

    if not Order.objects.filter(user=request.user):
        orders = None
        itemslist_temp = []
    else:
        orders = Order.objects.filter(user=request.user).values('item')
        orders = orders.values_list("item", flat=True)
        itemslist_temp, itemslist = [], []
        for order in orders:
            itemslist.append(order)
        for item in itemslist:
            itemslist_temp.append(Item.objects.filter(id=item))
        pizzas = []
        for item in itemslist_temp:
            pizzas.append(item.first())
            print(pizzas)


    context = {
        "pizzas": Pizza.objects.all(),
        "salads": Salad.objects.all(),
        "toppings": Topping.objects.all(),
        "orders": pizzas
    }

    return render(request, "index.html", context)


def add_topping(request):
    """
    Add topping to pizza on click of 'Save Toppings' button
    Directly create item and add it to Order, sepcific to current user.
    """

    # Index into list values
    for el in request.GET: value = el
    ids = value.split(",")
    print(ids, "IDS")
    # Get item name and pop from id-list
    name = ids[0]
    ids.pop(0)
    price = ids[0]
    ids.pop(0)
    print(price, "PRICE")

    # Convert strings to integers to get id's
    nums, tops = [], []
    [nums.append(int(num)) for num in ids]
    [tops.append(Topping.objects.filter(id=i)) for i in nums]

    # Get pizza object with pizza-name
    pizza = Pizza.objects.filter(name=name).first()

    # Make new item with these toppings
    item = Item(pizza=pizza)
    item.save()
    # item.pizza = pizza
    [print(top.first()) for top in tops]

    # Add all selected toppings to pizza
    [item.toppings.add(top.first()) for top in tops]

    # Check if this user already has an order
    order = Order.objects.filter(user=request.user).first()

    # Create new order for this user if it doesn't exist
    if order is None:
        order = Order(user=request.user)
        order.save()

    # Add item to orders for this user
    order.item.add(item)
    order.save()
    print(order, "order")

    return HttpResponse("Redirect index")
