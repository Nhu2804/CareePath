from django.shortcuts import render
from .models import TopIndustry, IndustryTrend
import json

from collections import OrderedDict

from django.db.models.functions import TruncDate
from django.db.models import Max

from django.db.models.functions import TruncDate
from django.db.models import Max

def market_trends_view(request):
    industries = TopIndustry.objects.all().order_by('-job_count')[:8]

    # Lấy 6 ngày khác nhau gần nhất (giảm dần ngày)
    distinct_dates = IndustryTrend.objects.annotate(date=TruncDate('updated_at')) \
        .values('date') \
        .annotate(latest_updated=Max('updated_at')) \
        .order_by('-date')[:6]

    # Lấy bản ghi mới nhất của từng ngày
    trends = IndustryTrend.objects.filter(updated_at__in=[d['latest_updated'] for d in distinct_dates])

    # Sắp xếp trends theo ngày tăng dần để biểu đồ hiển thị đúng
    trends = sorted(trends, key=lambda x: x.updated_at)

    trend_labels = [t.updated_at.strftime('%d/%m/%Y') for t in trends]
    trend_data = [t.trend_score for t in trends]

    industry_labels = [ind.name for ind in industries]
    industry_data = [ind.job_count for ind in industries]

    context = {
        'industries': industries,
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'industry_labels': json.dumps(industry_labels),
        'industry_data': json.dumps(industry_data),
    }
    return render(request, 'trend.html', context)






