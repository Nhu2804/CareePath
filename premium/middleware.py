from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

class PremiumRequiredMiddleware:
    """
    Middleware kiểm tra user có Premium còn hạn không.
    Nếu không, redirect về trang đăng ký Premium.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/premium-required/'):  # chỉnh prefix hoặc view cụ thể
            user = request.user
            if not user.is_authenticated:
                messages.warning(request, "Bạn cần đăng nhập để sử dụng tính năng này.")
                return redirect('login')

            if not user.is_premium or user.premium_expiry < timezone.now():
                messages.warning(request, "Bạn cần đăng ký Premium để truy cập tính năng này.")
                return redirect('premium:premium_home')

        return self.get_response(request)


class CheckPremiumExpiryMiddleware:
    """
    Middleware tự động hạ Premium nếu đã hết hạn mỗi khi user thực hiện request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_premium:
            if request.user.premium_expiry and request.user.premium_expiry < timezone.now():
                request.user.is_premium = False
                request.user.save()
        response = self.get_response(request)
        return response