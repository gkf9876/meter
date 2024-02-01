from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import InfoForm
from .models import Info


def index(request):
    info_list = Info.objects.filter(use_yn='Y').order_by('-create_date')
    context = {'info_list': info_list}
    return render(request, 'info/index.html', context)

@login_required(login_url='common:login')
def create(request):
    if request.method == 'POST':
        form = InfoForm(request.POST)
        if form.is_valid():
            info = form.save(commit=False)
            info.author = request.user
            info.create_date = timezone.now()
            info.save()
            return redirect('info:index')
    else:
        form = InfoForm()
    context = {'form': form}
    return render(request, 'info/form.html', context)

@login_required(login_url='common:login')
def modify(request, info_id):
    info = get_object_or_404(Info, pk=info_id)
    if request.user != info.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('info:index')
    if request.method == "POST":
        form = InfoForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            info.update_date = timezone.now()
            info.save()
            return redirect('info:index')
    else:
        form = InfoForm(instance=info)
    context = {'form': form}
    return render(request, 'info/form.html', context)

@login_required(login_url='common:login')
def delete(request, info_id):
    info = get_object_or_404(Info, pk=info_id)
    if request.user != info.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('info:index')
    info.modify_date = timezone.now()
    info.use_yn = 'N'
    info.save()
    return redirect('info:index')