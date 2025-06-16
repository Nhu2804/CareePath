from django.urls import path
from .views import premium_home

app_name = 'premium'

urlpatterns = [
    path('', premium_home, name='premium_home'),
]
