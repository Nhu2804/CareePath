from django.shortcuts import render

def premium_home(request):
    return render(request, 'premium.html')
