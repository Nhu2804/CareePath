# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser

# Form để TẠO MỚI người dùng (Trang Đăng Ký)
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Mật khẩu",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Tên", required=False)
    last_name = forms.CharField(label="Họ", required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2') 
        labels = {
            'username': 'Tên đăng nhập',
            'password1': 'Mật khẩu',
            'avatar': 'Ảnh đại diện',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    "Mật khẩu xác nhận không khớp.",
                    code='password_mismatch',
                )
        return password2
       
# Form để ĐĂNG NHẬP 
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Tên đăng nhập")
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)

# Form để THAY ĐỔI thông tin người dùng
class CustomUserChangeForm(UserChangeForm):
    password = None 

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email',
            'first_name': 'Tên',
            'last_name': 'Họ',
            'avatar': 'Ảnh đại diện',
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Địa chỉ email", widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nhập email của bạn',
    }))
