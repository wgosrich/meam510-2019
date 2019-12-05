from . import views
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name='home'),
    url(r'^ajax/update/$', views.update, name='update'),
]
