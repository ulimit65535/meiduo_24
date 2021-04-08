from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^smscode/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
]