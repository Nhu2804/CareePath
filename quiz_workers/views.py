from django.shortcuts import render

# Create your views here.

def gioi_thieu(request):
    return render(request, 'gioi_thieu_w.html')