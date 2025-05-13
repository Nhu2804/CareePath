from django.urls import path
from . import views

app_name = 'quiz_university'

urlpatterns = [
    path('gioi-thieu/', views.gioi_thieu, name='gioi_thieu_u'),
]
    