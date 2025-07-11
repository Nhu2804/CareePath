from django.db import models
from django.utils import timezone
class IndustryTrend(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trend_score = models.FloatField(default=0)
    job_growth = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    record_date = models.DateField(default=timezone.now)  # ✅ thêm dòng này

    def __str__(self):
        return self.name


class TopIndustry(models.Model):
    name = models.CharField(max_length=100)
    job_count = models.IntegerField(default=0)
    previous_job_count = models.IntegerField(default=0)
    job_growth_percent = models.FloatField(null=True, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



