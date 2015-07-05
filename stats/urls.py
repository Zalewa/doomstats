from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.front_page, name='front_page'),
    url(r'^engine/(?P<name>[ a-zA-Z]+)/$', views.engine_players, name='engine'),
    url(r'^engine/(?P<name>[ a-zA-Z]+)/wads/$', views.engine_wads, name='wads'),
    url(r'^engine/(?P<name>[ a-zA-Z]+)/servers/$', views.engine_servers, name='servers'),
    url(r'^about/$', views.about, name='about')
]
