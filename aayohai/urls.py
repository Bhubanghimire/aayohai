"""
URL configuration for aayohai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from accounts.urls import account_router
from system.urls import choice_router
from room.normal_user.urls import room_router


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((account_router.urls, 'accounts'), namespace='accounts')),
    path("api/type/", include((choice_router.urls, 'system'), namespace='system')),
    path("api/room/", include((room_router.urls, 'room'), namespace='room')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
