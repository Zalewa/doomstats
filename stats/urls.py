from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.front_page, name='front_page'),
    url(r'^engine/(?P<name>[ a-zA-Z]+)/$', views.engine, name='engine'),
    url(r'^about/$', views.about, name='about')
]
