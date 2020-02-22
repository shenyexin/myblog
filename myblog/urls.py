from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('blog/', include('blog.urls')),
    path('comment/', include('comment.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('likes/', include('likes.urls')),
    path('user/', include('user.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
