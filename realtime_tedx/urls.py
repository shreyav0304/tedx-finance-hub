from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tedx_finance.views import login_view, signup
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom auth routes (email verification)
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Password reset URLs (secure token-based)
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='emails/password_reset.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Include app URLs
    path('', include('tedx_finance.urls')),
]

# This is needed to properly serve uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

