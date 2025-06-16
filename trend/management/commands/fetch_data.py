import requests
from django.core.management.base import BaseCommand
from trend.models import TopIndustry, IndustryTrend
from datetime import datetime
import time
from random import uniform
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Fetch job market data from Adzuna API with pagination and update DB'

    def handle(self, *args, **kwargs):
        app_id = '160494d1'  # Thay bằng app_id của bạn
        app_key = '2eda2224bd01a8ea513c42037d15ef98'  # Thay bằng app_key của bạn
        country_code = 'gb'  # Quốc gia

        base_url = f'https://api.adzuna.com/v1/api/jobs/{country_code}/search/'

        industry_counts = {}
        total_pages = 20  # Số trang dữ liệu lấy

        for page in range(1, total_pages + 1):
            url = base_url + str(page)
            params = {
                'app_id': app_id,
                'app_key': app_key,
                'results_per_page': 100,
                'content-type': 'application/json',
            }
            response = requests.get(url, params=params)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch page {page}, status code: {response.status_code}"))
                self.stdout.write(self.style.ERROR(f"Response: {response.text}"))
                break

            data = response.json()
            jobs = data.get('results', [])

            for job in jobs:
                category = job.get('category', {}).get('label', 'Unknown')
                industry_counts[category] = industry_counts.get(category, 0) + 1

            time.sleep(1)  # tránh spam API quá nhanh

        # Icon mapping
        ICON_MAPPING = {
            'Teaching Jobs': 'fa-solid fa-chalkboard-teacher',
            'Engineering Jobs': 'fa-solid fa-cogs',
            'Healthcare & Nursing Jobs': 'fa-solid fa-heart-pulse',
            'Trade & Construction Jobs': 'fa-solid fa-building',
            'Social work Jobs': 'fa-solid fa-handshake',
            'Logistics & Warehouse Jobs': 'fa-solid fa-warehouse',
            'IT Jobs': 'fa-solid fa-laptop-code',
            'Sales Jobs': 'fa-solid fa-chart-line',
        }

        # Update TopIndustry
        for name, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            icon_class = ICON_MAPPING.get(name, 'fa-solid fa-briefcase')
            TopIndustry.objects.update_or_create(
                name=name,
                defaults={'job_count': count, 'icon': icon_class}
            )

        today = now().date()

        # Kiểm tra xem đã có dữ liệu ngày hôm nay chưa
        if IndustryTrend.objects.filter(updated_at__date=today).exists():
            self.stdout.write(self.style.WARNING(f"Data for {today} already exists. Skipping creation."))
        else:
            # Tạo 1 điểm dữ liệu mới cho ngày hôm nay
            IndustryTrend.objects.create(
                name=f"Trend ngày {today.strftime('%d/%m/%Y')}",
                description="Mô tả ví dụ",
                trend_score=round(uniform(0.3, 1.0), 2),
                job_growth=f"Tăng {round(uniform(5, 20), 2)}%/năm",
                updated_at=now()
            )
            self.stdout.write(self.style.SUCCESS(f"Created new trend data for {today}"))

        # Giữ lại tối đa 6 ngày dữ liệu gần nhất
        unique_dates = IndustryTrend.objects.values('updated_at__date').distinct().order_by('-updated_at__date')[:6]
        dates_to_keep = [d['updated_at__date'] for d in unique_dates]

        # Xóa các bản ghi có ngày không nằm trong 6 ngày gần nhất
        IndustryTrend.objects.exclude(updated_at__date__in=dates_to_keep).delete()

        self.stdout.write(self.style.SUCCESS('Successfully updated top industries and trends'))

        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining:
            self.stdout.write(self.style.SUCCESS(f"API requests remaining: {remaining}"))
