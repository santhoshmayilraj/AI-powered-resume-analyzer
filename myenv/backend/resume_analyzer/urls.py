from django.urls import path
from .views import upload_resume, signup,login

urlpatterns = [
    path('upload/', upload_resume, name='upload_resume'),  # Resume Upload API
    path('api/signup/', signup, name='signup'),  # Signup API
    path('api/login/',login,name='login'),
]
