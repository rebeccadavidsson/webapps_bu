from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("add_to_cart/<str:category>/<str:name>/<str:price>", views.add_to_cart, name="add_to_cart"),
    path('add_topping/', views.add_topping),
]
