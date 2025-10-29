from django.urls import path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:schedule_id>', views.detail, name='detail'),
    path('create', views.create, name='create'),
    path('modify/<int:schedule_id>', views.modify, name='modify'),
    path('delete/<int:schedule_id>', views.delete, name='delete'),
    path('detail_create/<int:schedule_id>', views.detail_create, name='detail_create'),
    path('detail_modify/<int:scheduledetail_id>', views.detail_modify, name='detail_modify'),
    path('detail_delete/<int:scheduledetail_id>', views.detail_delete, name='detail_delete'),
]