from django.urls import path

from . import views

app_name = 'habit'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:habit_id>/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
    path('modify/<int:habit_id>/', views.modify, name='modify'),
    path('delete/<int:habit_id>/', views.delete, name='delete'),
    path('detail_create/<int:habit_id>/', views.detail_create, name='detail_create'),
    path('detail_modify/<int:habitdetail_id>/', views.detail_modify, name='detail_modify'),
    path('detail_delete/<int:habit_id>/', views.detail_delete, name='detail_delete'),
]