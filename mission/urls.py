from django.urls import path

from . import views

app_name = 'mission'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:mission_id>/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
    path('modify/<int:mission_id>/', views.modify, name='modify'),
    path('delete/<int:mission_id>/', views.delete, name='delete'),
    path('detail_create/<int:mission_id>/', views.detail_create, name='detail_create'),
    path('detail_modify/<int:missiondetail_id>/', views.detail_modify, name='detail_modify'),
    path('detail_delete/<int:missiondetail_id>/', views.detail_delete, name='detail_delete'),
    path('vote/<int:mission_id>/', views.vote, name='vote'),
    path('detail/vote/<int:missiondetail_id>/', views.detail_vote, name='detail_vote'),
]