import os

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from .forms import UserForm
from .models import File


def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password, first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

def page_not_found(request, exception):
    return render(request, 'common/404.html', {})

def download_file(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    file_path = file.file.path
    if os.path.exists(file_path):
        # 파일 열기
        with open(file_path, 'rb') as buffer:
            # HttpResponse 객체 생성
            response = HttpResponse(buffer, content_type='application/octet-stream')
            # 파일 다운로드를 위한 Content-Disposition 헤더 설정
            response['Content-Disposition'] = "attachment; filename=%s" % file.name
            return response
    else:
        return HttpResponseNotFound("File not found")