from django.conf.urls import url

from . import views


urlpatterns = [
    # QQ第三方登录,拼接登录url
    url(r'^qq/authorization/$', views.OauthQQUrlView.as_view()),
    # QQ登录后的回调
    url(r'^qq/user/$', views.OauthQQUserView.as_view()),
]