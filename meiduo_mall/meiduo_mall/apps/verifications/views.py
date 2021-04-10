import logging
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status

# 从位于sys.path列表中的路径，直接导入即可
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants

logger = logging.getLogger('django')


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 0.从redis获取发送标记
        redis_conn = get_redis_connection('verify_codes')
        # 如果获取不到，会返回None
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message': '手机号频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)

        # 1.生成随机6位数字，不够补0
        sms_code = '%06d' % randint(0, 999999)

        # 2.创建redis管道，减少redis连接操作
        pl = redis_conn.pipeline()
        # 2.1 存储验证码到redis,300秒过期
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 2.2 存储一个标记，，标识此手机号已发送过短信，有效期60s
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 2.3 执行管道
        pl.execute()

        # 3.调用第三方sdk发送短信
        # CCP().send_template_sms(self, 手机号, [验证码， 过期时间], 模板id)
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)  # //表示整除
        logger.info('发送验证码:{}'.format(sms_code))
        # 4.响应
        return Response({'messsage': 'ok'})
