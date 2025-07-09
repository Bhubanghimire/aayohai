
from django.contrib import admin
from django.urls import path, include

from webapp.views.website import Homepage, Privacy, Terms
from webapp.views.admin import Dashboard

urlpatterns = [
    path("", Homepage.as_view(), name="home"),
    # path("about", About.as_view(), name="about"),
    path("privacy", Privacy.as_view(), name="privacy"),
    path("terms", Terms.as_view(), name="terms"),
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    ]