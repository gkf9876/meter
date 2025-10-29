import os, shutil, re
import time

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from urllib.parse import quote
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

@login_required(login_url='common:login')
def download_file(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    file_path = file.file.path
    if os.path.exists(file_path):
        # 파일 열기
        with open(file_path, 'rb') as buffer:
            # HttpResponse 객체 생성
            response = HttpResponse(buffer, content_type='application/octet-stream')
            # Content-Disposition 헤더 설정
            response['Content-Disposition'] = 'attachment; filename=%s' % quote(file.name)
            return response
    else:
        return HttpResponseNotFound("File not found")

@csrf_exempt
def temp_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        filename, ext = os.path.splitext(image.name)
        new_filename = f"{filename}_{int(time.time())}{ext}"  # UUID 사용

        file_instance = File()
        file_instance.name = new_filename
        file_instance.file = image
        file_path = os.path.join('editor', 'temp', new_filename)
        file_instance.file.save(file_path, image, save=True)

        image_url = f'/common/serve_image/{file_instance.id}'
        return JsonResponse({'location': image_url})

    return JsonResponse({'error': 'Failed to upload image'}, status=400)

@login_required(login_url='common:login')
def serve_image(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    file_path = file.file.path
    if os.path.exists(file_path):
        return HttpResponse(open(file_path, 'rb'), content_type='image/jpeg')
    else:
        return HttpResponseNotFound("File not found")

def move_temp_images_to_uploads(content):
    """본문 중 temp 이미지를 upload/editor로 이동"""
    file_ids = re.findall(r'/common/serve_image/(\d+)', content)
    for file_id in file_ids:
        temp_upload_file = get_object_or_404(File, pk=file_id)

        if os.path.exists(temp_upload_file.file.path):
            temp_file_path = temp_upload_file.file.path
            new_relative_path = os.path.join('uploads', 'editor', temp_upload_file.name)
            new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)

            # 디렉터리 생성
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

            # 파일 이동
            shutil.move(temp_file_path, new_full_path)

            # 파일 경로 갱신 (name은 DB에 저장되는 상대 경로임)
            temp_upload_file.file.name = new_relative_path
            temp_upload_file.save()
        else:
            return False

    return True