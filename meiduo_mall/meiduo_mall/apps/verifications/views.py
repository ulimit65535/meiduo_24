import logging
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import  Response

# 从位于sys.path列表中的路径，直接导入即可
from meiduo_mall.libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 1.生成随机6位数字，不够补0
        sms_code = '%06d' % randint(0, 999999)
        # 2.创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 3.存储验证码到redis,300秒过期
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 4.调用第三方sdk发送短信
        # CCP().send_template_sms(self, 手机号, [验证码， 过期时间], 模板id)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        logger.info('发送验证码:{}'.format(sms_code))
        # 5.响应
        return Response({'messsage': 'ok'})
