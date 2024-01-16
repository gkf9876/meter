from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from ..models import Todo

import logging
logger = logging.getLogger('todo')

@login_required(login_url='common:login')
def index(request):
    logger.info("INFO 레벨로 출력")
    check_yn = request.GET.get('check_yn', '')
    todo_tree = Todo.objects.filter(author_id=request.user.id, use_yn='Y')
    if check_yn:
        todo_tree = todo_tree.filter(check_yn=check_yn)
    context = {'todo_tree': todo_tree, 'check_yn':check_yn}
    return render(request, 'todo/todo_list.html', context)

@login_required(login_url='common:login')
def detail(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, author_id=request.user.id, use_yn='Y')
    context = {'todo': todo}
    return render(request, 'todo/todo_detail.html', context)