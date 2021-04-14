from django.conf.urls import url

from . import views


urlpatterns = [
    # QQ第三方登录,拼接登录url
    url(r'^qq/authorization/$', views.QQOauthUrlView.as_view()),
]