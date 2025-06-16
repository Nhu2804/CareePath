from django.urls import path
from . import views

app_name = 'trend'

urlpatterns = [
    path('', views.market_trends_view, name='trend'),  # ← view chính
]
