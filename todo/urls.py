from django.urls import path
from .views import base_views, todo_views, todo_detail_views

app_name = 'todo'

urlpatterns = [
    # base_views.py
    path('', base_views.index, name='todo_index'),
    path('<int:todo_id>/', base_views.detail, name='todo_detail'),

    # todo_views.py
    path('todo/create/', todo_views.todo_create, name='todo_create'),
    path('todo/modify/<int:todo_id>/', todo_views.todo_modify, name='todo_modify'),
    path('todo/delete/<int:todo_id>/', todo_views.todo_delete, name='todo_delete'),

    # todo_detail_views.py
    path('tododetail/create/<int:todo_id>', todo_detail_views.tododetail_create, name='tododetail_create'),
    path('tododetail/modify/<int:todo_detail_id>', todo_detail_views.tododetail_modify, name='tododetail_modify'),
    path('tododetail/delete/<int:todo_detail_id>', todo_detail_views.tododetail_delete, name='tododetail_delete'),
]