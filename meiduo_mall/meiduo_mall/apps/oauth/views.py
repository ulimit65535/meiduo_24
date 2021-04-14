from requests import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ

from django.conf import settings


class QQOauthUrlView(APIView):
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