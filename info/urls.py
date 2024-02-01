from django.urls import path

from . import views

app_name = 'info'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('modify/<int:info_id>/', views.modify, name='modify'),
    path('delete/<int:info_id>/', views.delete, name='delete'),
]