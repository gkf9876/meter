from django.urls import path

from . import views

app_name = 'meter'

urlpatterns = [
    path('', views.index, name='meter_index'),
    path('create/', views.create, name='meter_create'),
    path('update/', views.update, name='meter_update'),
]