import os
from celery import Celery

# 告诉celery，django配置文件去哪里找(因为tasks里使用了settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 1. 创建celery实例对象,参数为别名，可不写
celery_app = Celery('meiduo')

# 2. 加载配置文件
celery_app.config_from_object('celery_tasks.config')

# 3. 自动注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])