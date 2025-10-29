from django.urls import path
from .views import base_views, todo_views, todo_detail_views

app_name = 'todo'

urlpatterns = [
    # base_views.py
    path('', base_views.index, name='index'),
    path('<int:todo_id>', base_views.detail, name='detail'),

    # todo_views.py
    path('create', todo_views.todo_create, name='create'),
    path('modify/<int:todo_id>', todo_views.todo_modify, name='modify'),
    path('delete/<int:todo_id>', todo_views.todo_delete, name='delete'),
    path('dragdrop', todo_views.todo_dragdrop, name='dragdrop'),
    path('check/<int:todo_id>/<str:check_yn>', todo_views.todo_check, name='check'),

    # todo_detail_views.py
    path('detail_create/<int:todo_id>', todo_detail_views.tododetail_create, name='detail_create'),
    path('detail_modify/<int:todo_detail_id>', todo_detail_views.tododetail_modify, name='detail_modify'),
    path('detail_delete/<int:todo_detail_id>', todo_detail_views.tododetail_delete, name='detail_delete'),

]