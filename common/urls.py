from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('serve_image/<int:file_id>/', views.serve_image, name='serve_image'),
]