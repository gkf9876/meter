from django.urls import path

from . import views

app_name = 'health'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:health_id>', views.detail, name='detail'),
    path('create', views.create, name='create'),
    path('modify/<int:health_id>', views.modify, name='modify'),
    path('delete/<int:health_id>', views.delete, name='delete'),
    path('detail_create/<int:health_id>', views.detail_create, name='detail_create'),
    path('detail_modify/<int:healthdetail_id>', views.detail_modify, name='detail_modify'),
    path('detail_delete/<int:healthdetail_id>', views.detail_delete, name='detail_delete'),
    path('vote/<int:health_id>', views.vote, name='vote'),
    path('detail/vote/<int:healthdetail_id>', views.detail_vote, name='detail_vote'),
]