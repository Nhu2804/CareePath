from django.shortcuts import render
from .models import TopIndustry, IndustryTrend
import json
from django.db.models import Avg

def market_trends_view(request):
    industries = TopIndustry.objects.all().order_by('-job_count')[:8]

    trends = (
        IndustryTrend.objects
        .values('record_date')  # 👉 Dùng record_date thay vì TruncDate
        .annotate(trend_score_avg=Avg('trend_score'))
        .order_by('record_date')
    )

    trends = [t for t in trends if t['record_date'] is not None]

    trend_labels = [t['record_date'].strftime('%d/%m/%Y') for t in trends]
    trend_data = [round(t['trend_score_avg'], 2) for t in trends]

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
