from django.urls import path
from .views import upload_resume, signup

urlpatterns = [
    path('upload/', upload_resume, name='upload_resume'),  # Resume Upload API
    path('api/signup/', signup, name='signup'),  # Signup API
]
