from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings


# Create your models here.
class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_email_verify_url(self):
        """生成邮箱激活链接"""

        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)
        data = {
            'user_id': self.id,
            'email': self.email
        }
        token = serializer.dumps(data).decode()

        return 'http://' + settings.FRONT_END + '/success_verify_email.html?token=' + token

    @staticmethod
    def check_verify_email_token(token):
        """验证邮箱激活token"""
        serializer = TJWSSerializer(settings.SECRET_KEY, 3600 * 24)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
