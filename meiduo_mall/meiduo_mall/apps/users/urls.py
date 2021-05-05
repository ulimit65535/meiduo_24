from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from . import views


urlpatterns = [
    # 注册用户
    url(r'^users/$', views.UserView.as_view()),
    # 判断用户名是否已注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否已注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # JWT登录
    url(r'authorizations/$', obtain_jwt_token),  # 内部认证代码仍是Django, 登录成功生成token响应

    # 获取用户详情
    url(r'^user/$', views.UserDetailView.as_view()),
    # 更新邮箱
    url(r'^email/$', views.EmailView.as_view()),
    # 邮箱激活验证
    url(r'^email/verification/$', views.EmailVerifyView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='address')
urlpatterns += router.urls