from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    path('', views.premium_home, name='premium_home'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/', views.checkout_success_view, name='checkout_success'),
]
