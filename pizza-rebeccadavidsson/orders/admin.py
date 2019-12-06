from django.contrib import admin
from orders.models import *

# Register your models here.
admin.site.register(Pizza)
admin.site.register(Salad)
admin.site.register(Topping)
admin.site.register(Item)
admin.site.register(Order)
