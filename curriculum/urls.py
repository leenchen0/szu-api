from django.conf.urls import url

from curriculum import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^student/$', views.queryStudent),
]
