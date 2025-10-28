import os
import time

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
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        filename, ext = os.path.splitext(image.name)
        new_filename = f"{filename}_{int(time.time())}{ext}"  # UUID 사용

        file_instance = File()
        file_instance.name = new_filename
        file_instance.file = image
        file_instance.save()

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
    """글 내용에 포함된 temp 이미지들을 uploads 폴더로 이동"""
    import re
    pattern = r'/media/temp/([a-zA-Z0-9_.-]+)'
    matches = re.findall(pattern, content)
    for filename in matches:
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', filename)
        perm_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        if os.path.exists(temp_path):
            os.makedirs(os.path.dirname(perm_path), exist_ok=True)
            shutil.move(temp_path, perm_path)
            # HTML 경로 교체
            content = content.replace(f'/media/temp/{filename}', f'/media/uploads/{filename}')
    return content