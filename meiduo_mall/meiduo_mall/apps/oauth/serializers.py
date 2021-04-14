from django_redis import get_redis_connection
from rest_framework import serializers
from .utils import check_save_user_token
from users.models import User
from .models import OauthQQUser


class OauthQQUserSerializer(serializers.Serializer):
    """
    openid 绑定用户的序列化器
    这个序列化器只用来做反序列化，故不需指定字段读写属性
    """

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 1.把加密的openid取出解密
        access_token = attrs.pop('access_token')

        # 1.1把解密后的openid重新添加到attrs字典中，提供给后面create方法绑定使用
        openid = check_save_user_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid无效')
        attrs['openid'] = openid

        # 2.校验验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        # redis取出的数据都是bytes类型,先判断是否是None，不然不能调用decode方法
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        # 3.拿手机号查询user表，如果已存在，再判断密码是否正确
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            if user.check_password(attrs['password']):
                # 如果用户已存在，且密码正确，将user对象存储到反序列化的大字典中备后期使用
                attrs['user'] = user
            else:
                raise serializers.ValidationError('密码错误')

        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        # 如果validated_data存在user，说明用户已存在
        if user:
            pass
        else:
            # 创建新用户，偷懒，新的用户名直接用手机号
            user = User(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile')
            )
            user.set_password(validated_data.get('password'))
            user.save()
            # openid与user绑定
            OauthQQUser.objects.create(
                openid=validated_data.get('openid'),
                user=user   # 或写为:user_id=user.id
            )

        return user
