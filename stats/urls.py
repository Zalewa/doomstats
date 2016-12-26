from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.front_page, name='front_page'),
    url(r'^engine/(?P<name>[ a-zA-Z0-9]+)/$', views.engine_players, name='engine'),
    url(r'^engine/(?P<name>[ a-zA-Z0-9]+)/wads/$', views.engine_wads, name='wads'),
    url(r'^engine/(?P<name>[ a-zA-Z0-9]+)/servers/$', views.engine_servers, name='servers'),
    url(r'^about/$', views.about, name='about')
]
