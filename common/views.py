import os
import time

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from urllib.parse import quote
from django.conf import settings
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
        save_path = os.path.join(settings.MEDIA_ROOT, 'editor', new_filename)

        with open(save_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        image_url = f'{settings.MEDIA_URL}/editor/{new_filename}'
        return JsonResponse({'location': image_url})

    return JsonResponse({'error': 'Failed to upload image'}, status=400)
