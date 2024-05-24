from django.contrib import admin
from django.urls import path, include

from notice.views import NoticeListWebView

app_name = 'notice'

urlpatterns = [
    path('list/', NoticeListWebView.as_view(), name='notice-list'),
]
