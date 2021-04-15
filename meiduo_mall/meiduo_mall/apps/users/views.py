from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer
from .models import User


# Create your views here.


class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器
    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    """判断用户名是否已注册"""

    def get(self, request, username):
        # 查询user表
        count = User.objects.filter(username=username).count()

        # 包装响应体数据
        data = {
            'username': username,
            'count': count
        }

        # 响应
        return Response(data)


class MobileCountView(APIView):
    """判断手机号是否已注册"""

    def get(self, request, mobile):
        # 查询user表
        count = User.objects.filter(mobile=mobile).count()

        # 包装响应体数据
        data = {
            'mobile': mobile,
            'count': count
        }

        # 响应
        return Response(data)


class UserDetailView(RetrieveAPIView):
    """用户详细信息展示"""
    serializer_class = UserDetailSerializer
    # queryset = User.objects.all() # 重写了父亲的get_object方法，不再需要queryset
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """重写父类GenericAPIView的get_object方法，返回要展示的用户模型对象"""
        return self.request.user


class EmailView(UpdateAPIView):
    """更新用户邮箱"""
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """重写父类GenericAPIView的get_object方法，返回要展示的用户模型对象"""
        return self.request.user


class EmailVerifyView(APIView):
    """激活邮箱"""

    def get(self, request):
        # 获取前端传入的token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'},status=status.HTTP_400_BAD_REQUEST)
        # token解密，并查询对应的user
        user = User.check_verify_email_token(token)
        # 修改当前user的email_active为true
        if user is None:
            return Response({'message': '激活失败'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        # 响应
        return Response({'message': 'ok'})
