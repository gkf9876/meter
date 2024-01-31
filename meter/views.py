import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, ExpressionWrapper, F, fields, DateTimeField
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from .models import Study, Meter


@login_required(login_url='common:login')
def index(request):
    study_list = Study.objects.order_by('-create_date').filter(author_id=request.user.id)
    context = {'study_list': study_list}
    return render(request, 'meter/index.html', context)

def create(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        study_id = json_data.get('study_id', None)
        memo = json_data.get('memo', None)
        if not study_id:
            return JsonResponse({'error': 'Invalid study_id'}, status=400)
        try:
            study = get_object_or_404(Study, id=study_id)
            meter = Meter()
            meter.author = request.user
            meter.start_date = timezone.now()
            meter.end_date = timezone.now()
            meter.memo = memo
            meter.study = study
            meter.save()
            response_data = {'meter_id':meter.id, 'start_date':meter.start_date, 'end_date':meter.end_date, 'message': '데이터베이스 값이 성공적으로 업데이트되었습니다.'}
        except Study.DoesNotExist:
            return JsonResponse({'error': 'Data not found'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        return JsonResponse(response_data)
    else:
        print("Invalid request")
        return JsonResponse({'error': 'Invalid request'}, status=400)

def update(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        meter_id = json_data.get('meter_id', None)
        memo = json_data.get('memo', None)
        if not meter_id:
            return JsonResponse({'error': 'Invalid meter_id'}, status=400)
        try:
            meter = get_object_or_404(Meter, id=meter_id)
            current_time = timezone.now()
            one_day_ago = current_time - timezone.timedelta(days=1)

            # 24:00 지날때 처리
            if meter.start_date.day < current_time.day:
                meter.author = request.user
                meter.end_date = timezone.datetime(one_day_ago.year, one_day_ago.month, one_day_ago.day, 23, 59, 59)
                meter.memo = memo
                meter.save()

                temp = Meter()
                temp.author = request.user
                temp.start_date = timezone.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0)
                temp.end_date = current_time
                temp.memo = memo
                temp.study = meter.study
                temp.save()

                meter = temp
            else:
                meter.author = request.user
                meter.end_date = current_time
                meter.memo = memo
                meter.save()
            response_data = {'meter_id':meter.id, 'start_date':meter.start_date, 'end_date' : meter.end_date, 'message': '데이터베이스 값이 성공적으로 업데이트되었습니다.'}
            return JsonResponse(response_data)
        except Meter.DoesNotExist:
            return JsonResponse({'error': 'Data not found'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        print("Invalid request")
        return JsonResponse({'error': 'Invalid request'})

@login_required(login_url='common:login')
def chart(request):
    study_list = Study.objects.filter(author_id=request.user.id).order_by('-create_date')
    study_id = request.GET.get('study_id', '')
    labels = []
    data = []
    if study_id:
        study = get_object_or_404(Study, pk=study_id, author_id=request.user.id)
        study_id = study.id
        today = timezone.now()
        start_date = today - timezone.timedelta(days=15)
        seconds_expression = ExpressionWrapper(F('end_date') - F('start_date'),output_field=fields.DurationField())
        meter_list = (Meter.objects.filter(author_id=request.user.id, study_id=study.id, end_date__range=(start_date, today))
                      .annotate(day_seconds=seconds_expression)
                      .annotate(truncated_date=TruncDate('end_date', output_field=DateTimeField()))
                      .values('truncated_date')
                      .annotate(total_seconds=Sum('day_seconds'))
                      .order_by('truncated_date'))
        truncated_date = meter_list.values_list('truncated_date', flat=True)
        labels = [td.strftime('%Y-%m-%d') for td in truncated_date]
        total_seconds = meter_list.values_list('total_seconds', flat=True)
        data = [int(ts.total_seconds())/60 for ts in total_seconds]
    context = {'study_list': study_list, 'labels': labels, 'data': data, 'study_id':study_id}
    return render(request, 'meter/chart.html', context)