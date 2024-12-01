from django.conf.urls.static import static 
from django.urls import path, re_path, include
from django.contrib import admin
from corelims import settings

from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'patients', views.PatientsView, 'patients')


admin.site.site_header = 'corelimsm admin'
urlpatterns = [
    re_path(r"^", include("corelab.urls")),
    path(r"api_react/", include(router.urls)),
    re_path(r"avatar/", include("avatar.urls")),
    re_path(r"^admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
