import re
from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User
from celery_tasks.email.tasks import send_verify_email


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    # 需要序列化的字段: ['id', 'username', 'mobile', 'token']
    # 需要反序列化的字段: ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User    # 从User模型中映射序列化器字段
        # fields = '__all__'
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token']
        extra_kwargs = {  # 修改字段属性
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,  # 只做反序列化
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """单独校验手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误')
        return value

    def validate_allow(self, value):
        """是否同意协议检验"""
        if value != "true":
            raise serializers.ValidationError('请同意用户协议')
        return value

    # 联合检验
    def validate(self, attrs):
        # 检验两个密码是否相同
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码输入不一致')

        # 校验验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        # redis取出的数据都是bytes类型,先判断是否是None，不然不能调用decode方法
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validate_data):
        """重写create方法，移除不需要写的属性字段"""
        del validate_data['password2']
        del validate_data['sms_code']
        del validate_data['allow']

        password = validate_data.pop('password')  # 删除明文密码
        user = User(**validate_data)
        user.set_password(password)  # 把密码加密后再赋值给user的password属性
        user.save()

        # 注册后，自动登录，需要生成jwt，响应给前端
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)  # 传入用户模型对象，生成payload部分
        token = jwt_encode_handler(payload)  # 传入截荷，生成完整的jwt
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    """更新邮箱序列化器"""
    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True  # 重写User的email属性，反序列化校验时，必须有该字段
            }
        }

    def update(self, instance, validated_data):
        """重写update方法，借用此时机发激活邮件"""

        # 后续逻辑调用父类update方法
        instance = super(EmailSerializer, self).update(instance, validated_data)

        # 发送邮件验证邮箱
        verify_url = instance.generate_email_verify_url()
        send_verify_email.delay(instance.email, verify_url)  # 添加异步任务

        return instance
