from django.urls import path

from . import views

app_name = 'doit'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:doit_id>', views.detail, name='detail'),
    path('create', views.create, name='create'),
    path('modify/<int:doit_id>', views.modify, name='modify'),
    path('delete/<int:doit_id>', views.delete, name='delete'),
    path('detail_create/<int:doit_id>', views.detail_create, name='detail_create'),
    path('detail_modify/<int:doitdetail_id>', views.detail_modify, name='detail_modify'),
    path('detail_delete/<int:doitdetail_id>', views.detail_delete, name='detail_delete'),
    path('vote/<int:doit_id>', views.vote, name='vote'),
    path('detail/vote/<int:doitdetail_id>', views.detail_vote, name='detail_vote'),
]