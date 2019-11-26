from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.services_list, name='post_list'),
]