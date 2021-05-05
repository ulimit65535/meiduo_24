from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin

from .serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer
from .models import User, Address
from . import constants


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


class AddressViewSet(UpdateModelMixin, GenericViewSet):
    """
    用户收货地址增删改查
    这里不继承ModelViewSet，是因为要自己实现create和list和delete
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        user = request.user
        # count = Address.objects.filter(user=user).count()
        count = user.addresses.all().count()
        # 用户收货地址有上限
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '收货地址已达上限'}, stauts=status.HTTP_400_BAD_REQUEST)
        # 创建序列化器进行反序列化
        serializer = self.get_serializer(data=request.data)
        # 调用序列化器的is_valid方法
        serializer.is_valid(raise_exception=True)
        # 调用序列化器save
        serializer.save()
        # 响应
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT /addresses/pk/title/
    # 视图集的as_view默认只帮我们实现了增删改查的路由，新增的方法需要加上装饰器
    #  detail: 声明该action的路径是否与单一资源对应，及是否是xxx/<pk>/action方法名/
    #         True 表示路径格式是xxx/<pk>/action方法名/
    #         False 表示路径格式是xxx/action方法名/
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改地址标题"""
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # PUT /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """修改默认地址"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)




