from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings


def generate_save_user_token(openid):
    """
    对openid进行加密
    :param openid:
    :return:字典加密后生成的字符串
    """
    # 1.创建加密的序列化对象
    serializer = TJWSSerializer(settings.SECRET_KEY, 600)

    # 2.调用dumps(json字典)方法进行加密
    data = {'openid': openid}
    token = serializer.dumps(data)

    # 3.把加密后的openid返回,加密后的数据默认为bytes类型，调用decode转换为字符串
    return token.decode()


def check_save_user_token(access_token):
    """
    传入token，解密拿到openid
    :param access_token:密文
    :return:openid or None
    """
    # 1.创建加密的序列化对象
    serializer = TJWSSerializer(settings.SECRET_KEY, 600)
    # 2.loads方法进行加密
    try:
        data = serializer.loads(access_token)
    except BadData:
        # 或超出过期时间，无法解密
        return None
    else:
        return data.get('openid')
