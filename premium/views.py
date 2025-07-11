from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

def premium_home(request):
    return render(request, 'premium.html')

@login_required
def checkout_view(request):
    if request.method == 'POST':
        user = request.user

        # Gán Premium trực tiếp trên CustomUser
        user.is_premium = True
        user.premium_expiry = timezone.now() + timedelta(days=14)
        user.save()

        messages.success(request, "Đăng ký Premium thành công! Bạn có 14 ngày trải nghiệm miễn phí.")
        return redirect('premium:checkout_success')

    return render(request, 'premium/checkout.html')

@login_required
def checkout_success_view(request):
    return render(request, 'premium/checkout_success.html')
