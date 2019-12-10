from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('add_topping/', views.add_topping),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('delete/<str:order>', views.delete, name="delete")
]
