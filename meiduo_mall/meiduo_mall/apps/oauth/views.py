import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework_jwt.settings import api_settings

from .models import OauthQQUser
from .serializers import OauthQQUserSerializer
from .utils import generate_save_user_token

logger = logging.getLogger('django')


class OauthQQUrlView(APIView):
    """拼接QQ第三方登录url"""

    def get(self, request):
        # 提取前端传入的next参数，记录用户referer
        # next = request.query_params.get('next') or '/'
        next = request.query_params.get('next', '/')  # get(self, key, default=None)

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        login_url = oauth.get_qq_url()
        return Response({'login_url': login_url})


class OauthQQUserView(APIView):
    """QQ登录成功后的回调处理"""

    def get(self,request):
        # 获取前端传入的code
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        # 创建工具类对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=None)
        try:
            # 用code向qq服务器请求获取access_token
            access_token = oauth.get_access_token(code)
            # 用access_token向qq服务器请求获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return Response({'message': 'QQ服务器不可用'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 查询数据库有没有这个openid
        try:
            oauth_qq_user = OauthQQUser.objects.get(openid=openid)
        except OauthQQUser.DoesNotExist:
            # openid未绑定用户，把openid加密后传给前端，让前端暂存一会，等待绑定时使用
            access_token_openid = generate_save_user_token(openid)
            return Response({'access_token': access_token_openid})
        else:
            # openid已绑定过用户，直接登录成功，给前端返回JWT
            user = oauth_qq_user.user   # 获取到openid关联的用户
            # 生成jwt，响应给前端
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)  # 传入用户模型对象，生成payload部分
            token = jwt_encode_handler(payload)  # 传入截荷，生成完整的jwt

            return Response({
                'token': token,
                'username': user.username,
                'user_id': user.id
            })

    def post(self, request):
        """openid绑定用户接口"""
        # 创建序列化器进行反序列化
        serializer = OauthQQUserSerializer(data=request.data)
        # 调用is_valid方法进行校验
        serializer.is_valid(raise_exception=True)
        # 调用序列化器save方法，返回值是序列化器create/update方法的返回值
        user = serializer.save()
        # 生成jwt保存会话状态
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)  # 传入用户模型对象，生成payload部分
        token = jwt_encode_handler(payload)  # 传入截荷，生成完整的jwt
        # 响应
        return Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })