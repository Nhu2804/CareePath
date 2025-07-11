from social_core.exceptions import AuthException
from social_core.backends.google import GoogleOAuth2
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import requests

User = get_user_model()

def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Tự động liên kết tài khoản Google OAuth với user đã tồn tại bằng email.
    """
    if user:
        return None

    email = details.get('email')
    if email:
        try:
            user = User.objects.get(email=email)
            return {'user': user}
        except User.DoesNotExist:
            return None

def save_avatar_from_google(backend, user, response, *args, **kwargs):
    print("Backend name:", backend.name)
    print("Response data:", response)

    if backend.name != 'google-oauth2':
        return

    url = response.get('picture')
    print("Avatar URL:", url)

    if url and user and (not user.avatar or user.avatar.name == 'avatars/default_avatar.png'):
        try:
            avatar_content = requests.get(url).content
            user.avatar.save(
                f"{user.username}_google_avatar.jpg",
                ContentFile(avatar_content),
                save=True
            )
            print("Avatar saved successfully.")
        except Exception as e:
            print(f"Lỗi khi lấy avatar Google: {e}")