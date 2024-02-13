from django.urls import path
from . import views

app_name = 'memorization'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:memorization_id>/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
    path('modify/<int:memorization_id>/', views.modify, name='modify'),
    path('delete/<int:memorization_id>/', views.delete, name='delete'),
]