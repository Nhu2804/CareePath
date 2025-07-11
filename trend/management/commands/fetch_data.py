# fetch_data.py (FULL CODE FIXED)

from django.core.management.base import BaseCommand
from trend.models import TopIndustry, IndustryTrend
from django.utils.timezone import now
from random import uniform
import requests
import time

class Command(BaseCommand):
    help = 'Fetch job market data from Adzuna API with pagination and update DB'

    def handle(self, *args, **kwargs):
        app_id = '160494d1'  # Replace with your Adzuna app_id
        app_key = '2eda2224bd01a8ea513c42037d15ef98'  # Replace with your Adzuna app_key
        country_code = 'gb'
        base_url = f'https://api.adzuna.com/v1/api/jobs/{country_code}/search/'

        industry_counts = {}
        total_pages = 2  # For testing; adjust to 20+ when stable

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
                self.stdout.write(self.style.ERROR(f"Failed to fetch page {page}, status: {response.status_code}"))
                break
            data = response.json()
            jobs = data.get('results', [])

            for job in jobs:
                category = job.get('category', {}).get('label', 'Unknown')
                industry_counts[category] = industry_counts.get(category, 0) + 1

            time.sleep(1)

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

        for name, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            icon_class = ICON_MAPPING.get(name, 'fa-solid fa-briefcase')
            TopIndustry.objects.update_or_create(
                name=name,
                defaults={'job_count': count, 'icon': icon_class}
            )

        today = now().date()
        
        if not IndustryTrend.objects.filter(updated_at__date=today).exists():
            IndustryTrend.objects.create(
                name=f"Trend ngày {today.strftime('%d/%m/%Y')}",
                description="Mô tả tự động từ fetch_data",
                trend_score=round(uniform(0.3, 1.0), 2),
                job_growth=f"Tăng {round(uniform(5, 20), 2)}%/năm",
                record_date=today
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created new trend data for {today}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Data for {today} already exists. Skipping creation."))

        # Clean up old data (keep max 6 days)
        unique_dates = IndustryTrend.objects.values_list('record_date', flat=True).distinct().order_by('-record_date')[:6]
        dates_to_keep = list(unique_dates)
        deleted_count, _ = IndustryTrend.objects.exclude(record_date__in=dates_to_keep).delete()

        
        self.stdout.write(self.style.SUCCESS(f"🧹 Cleaned {deleted_count} old records, kept {len(dates_to_keep)} recent days."))
        self.stdout.write(self.style.SUCCESS('✅ Successfully updated top industries and trends.'))
