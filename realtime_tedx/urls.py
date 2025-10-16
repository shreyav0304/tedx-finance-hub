from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line tells the main project to include Django's built-in login/logout URLs
    path('accounts/', include('django.contrib.auth.urls')),
    
    # This line tells the main project to hand off any matching requests to your app's urls.py file
    path('', include('tedx_finance.urls')),
]

# This is needed to properly serve uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

