from django.urls import path
from . import views

app_name = 'quiz_workers'

urlpatterns = [
    path('gioi-thieu/', views.gioi_thieu, name='gioi_thieu_w'),
]
    