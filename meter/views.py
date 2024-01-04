from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from .models import Study, Meter


@login_required(login_url='common:login')
def index(request):
    study_list = Study.objects.order_by('-create_date').filter(author_id=request.user.id)
    context = {'study_list': study_list}
    return render(request, 'meter/meter_index.html', context)

def create(request):
    if request.method == 'POST':
        study_id = request.POST.get('study_id', None)

        if not study_id:
            return JsonResponse({'error': 'Invalid study_id'}, status=400)

        try:
            study = get_object_or_404(Study, id=study_id)

            meter = Meter()
            meter.author = request.user
            meter.start_date = timezone.now()
            meter.end_date = timezone.now()
            meter.study = study
            meter.save()

            response_data = {'meter_id':meter.id, 'message': '데이터베이스 값이 성공적으로 업데이트되었습니다.'}
        except Study.DoesNotExist:
            return JsonResponse({'error': 'Data not found'}, status=400)
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def update(request):
    if request.method == 'POST':
        meter_id = request.POST.get('meter_id', None)

        if not meter_id:
            return JsonResponse({'error': 'Invalid meter_id'}, status=400)

        try:
            meter = get_object_or_404(Meter, id=meter_id)
            meter.author = request.user
            meter.end_date = timezone.now()
            meter.save()

            response_data = {'message': '데이터베이스 값이 성공적으로 업데이트되었습니다.'}
            return JsonResponse(response_data)
        except Meter.DoesNotExist:
            return JsonResponse({'error': 'Data not found'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'})