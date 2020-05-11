from django.conf.urls import url
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('rss/<str:service>', views.rss_item, name='rss_item'),
    path('message/<str:msg>', views.message, name='message'),
    path('message/', views.message_empty, name='message_empty'),
    path('rss/', views.rss_list, name='rss_list'),
    path('pocasie/', views.weather_prompt, name='weather'),
    path('weather_engine/', views.weather, name='weather_engine'),
    path('', views.services_list, name='post_list'),
    path('kontakty_uniza/', views.contacts_prompt, name='contacts'),
    path('contacts_engine/', views.contacts_engine, name='contacts_engine'),
    path('contact/', views.contact, name='contact'),
    path('contact_dialer/<str:numbers>', views.contact_dialer, name='dialer'),
    path('contact_dialer/', views.contact_dialer_empty, name='dialer_empty'),
    path('kontakty_zlate_stranky/', views.contacts_prompt_zlatestranky, name='contacts_zoznam'),
    path('contacts_engine_zlatestranky/', views.contacts_engine_zlatestranky, name='contacts_engine_zoznam'),
    path('contact_zlatestranky/', views.contact_zlatestranky, name='contact_zoznam'),
]
