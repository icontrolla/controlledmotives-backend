import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('profiles.urls')),
]

# Serve media in development or on Render
if settings.DEBUG or os.environ.get('RENDER'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
