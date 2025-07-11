from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)  # Tự động đăng nhập sau khi đăng ký
            return redirect('home')  # Thay 'home' bằng tên URL bạn muốn
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # Phần xử lý POST cho form đăng nhập giữ nguyên
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()

    # 👇 THÊM DÒNG NÀY: Tạo một instance của form reset password
    password_reset_form = PasswordResetForm()

    # 👇 CẬP NHẬT CONTEXT: Truyền cả 2 form ra template
    context = {
        'form': form,
        'password_reset_form': password_reset_form
    }
    
    return render(request, 'login.html', context)

@require_POST # Chỉ cho phép phương thức POST
def ajax_password_reset_view(request):
    # Kiểm tra xem có phải là request AJAX không (tùy chọn nhưng là good practice)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Tùy chỉnh các tham số để gửi email
            # Quan trọng: cần có `request=request` để Django có thể tạo link tuyệt đối
            form.save(
                request=request,
                from_email=None, # Sử dụng DEFAULT_FROM_EMAIL trong settings.py
                email_template_name='registration/password_reset_email.txt',  # fallback plain text
                subject_template_name='registration/password_reset_subject.txt',
                html_email_template_name='registration/password_reset_email.html',  # ✅ gửi email HTML
            )

            return JsonResponse({'status': 'success', 'message': 'Vui lòng kiểm tra email để đặt lại mật khẩu.'})
        else:
            # Trả về lỗi nếu form không hợp lệ
            return JsonResponse({'status': 'error', 'errors': form.errors.get_json_data()}, status=400)
    
    # Nếu không phải AJAX, trả về lỗi
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Mật khẩu đã được thay đổi thành công!'})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # ✅ Gửi về một dictionary chứa TẤT CẢ các lỗi
            # JavaScript sẽ tự xử lý việc hiển thị
            return JsonResponse({
                'status': 'error', 
                'errors': form.errors.get_json_data()
            }, status=400)
            
        return super().form_invalid(form)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('home')
    return render(request, 'delete_account_confirm.html')


@login_required
@require_POST
def ajax_update_avatar(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Sử dụng một form đơn giản chỉ chứa trường avatar
        # Chúng ta có thể tạo một form mới hoặc tái sử dụng CustomUserChangeForm
        # Ở đây, ta sẽ truy cập trực tiếp để đơn giản hóa
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        
        # Chỉ kiểm tra và lưu trường avatar
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
            request.user.save(update_fields=['avatar'])
            
            # Trả về đường dẫn của ảnh mới để JS cập nhật giao diện
            return JsonResponse({'status': 'success', 'new_avatar_url': request.user.avatar.url})

        # Nếu không có file nào được gửi
        return JsonResponse({'status': 'error', 'message': 'Không có file nào được chọn.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)


@login_required
def ajax_update_profile(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = request.user
        
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        # --- Validation đơn giản ---
        if not first_name or not last_name:
            return JsonResponse({'status': 'error', 'message': 'Họ và Tên không được để trống.'})

        # Kiểm tra định dạng email
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Địa chỉ email không hợp lệ.'})

        # Kiểm tra email đã tồn tại chưa (trừ email của chính user này)
        if request.user._meta.model.objects.filter(email=email).exclude(pk=user.pk).exists():
             return JsonResponse({'status': 'error', 'message': 'Địa chỉ email này đã được sử dụng.'})

        # --- Cập nhật thông tin ---
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cập nhật thành công!',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)