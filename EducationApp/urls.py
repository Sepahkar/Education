from django.urls import path
from . import views

app_name = 'EducationApp'

urlpatterns = [
    path('', views.welcome, name='welcome'),
]