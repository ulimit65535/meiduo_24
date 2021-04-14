from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings


def generate_save_user_token(openid):
    """对openid进行加密"""
    # 1.创建加密的序列化对象
    serializer = TJWSSerializer(settings.SECRET_KEY, 600)

    # 2.调用dumps(json字典)方法进行加密
    data = {'openid': openid}
    token = serializer.dump(data)

    # 3.把加密后的openid返回,加密后的数据默认为bytes类型，调用decode转换为字符串
    return token.decode()