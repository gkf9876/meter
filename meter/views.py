from django.contrib.auth.decorators import login_required
from django.db.models import Sum, ExpressionWrapper, F, fields, Func
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
                      .annotate(truncated_date=TruncDate('end_date'))
                      .values('truncated_date')
                      .annotate(day_seconds=seconds_expression)
                      .annotate(total_seconds=Sum('day_seconds'))
                      .order_by('truncated_date'))
        truncated_date = meter_list.values_list('truncated_date', flat=True)
        labels = [td.strftime('%Y-%m-%d') for td in truncated_date]
        total_seconds = meter_list.values_list('total_seconds', flat=True)
        data = [int(ts.total_seconds())/60 for ts in total_seconds]
    context = {'study_list': study_list, 'labels': labels, 'data': data, 'study_id':study_id}
    return render(request, 'meter/meter_chart.html', context)