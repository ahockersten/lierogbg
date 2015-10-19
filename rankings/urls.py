"""
URLs for rankings
"""
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    'rankings.views',
    url(r'^/*$', views.PlayerList.as_view()),
)
