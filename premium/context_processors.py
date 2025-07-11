from django.utils import timezone

def premium_status(request):
    notice = None
    if request.user.is_authenticated and request.user.is_premium and request.user.premium_expiry:
        remaining = request.user.premium_expiry - timezone.now()
        if remaining.days <= 2 and remaining.days >= 0:
            notice = f"⚠️ Gói Premium của bạn sẽ hết hạn sau {remaining.days} ngày (vào {request.user.premium_expiry.strftime('%d/%m/%Y')}). Vui lòng gia hạn để không gián đoạn dịch vụ."
    return {'premium_notice': notice}
