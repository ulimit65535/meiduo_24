import re

from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录视图的构造顺应数据函数，追加username,id"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

def get_user_by_account(account):
    """
    通过传入的账号，动态获取user模型对象
    :param account:手机号或用户名
    :return: user模型对象或None
    """
    try:
        if re.match(r'1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """修改django认证类，为了实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取到user
        user = get_user_by_account(username)

        # 判断用户是否存在，密码是否正确
        if user and user.check_password(password):
            # 返回user
            return user
