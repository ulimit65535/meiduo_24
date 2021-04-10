# celery配置文件

# 某个程序中出现的队列，在broker中不存在，则立刻创建它
CELERY_CREATE_MISSING_QUEUES = True

# 指定任务队列的地址
BROKER_URL = 'redis://192.168.1.254:6379/7'

# 并发workers数
CELERYD_CONCURRENCY = 1

CELERY_TIMEZONE = 'Asia/Shanghai'

CELERYD_FORCE_EXECV = True  # 非常重要,有些情况下可以防止死锁

CELERYD_PREFETCH_MULTIPLIER = 1

CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露

CELERY_DISABLE_RATE_LIMITS = True  # 关闭任务限速

# CELERYD_TASK_TIME_LIMIT = 60  # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死
# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 90}  # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行

################################################
"""
# 启动worker的命令
# 注意位于项目根目录执行，因为tasks.py里的import是从项目根目录开始的
# celery -A celery_tasks.main worker -l info

# win10有bug，解决方法:
# pip install eventlet
# celery -A celery_tasks.main worker -l info -P eventlet
"""

"""
# *** 定时器 ***
# nohup celery beat -s /var/log/boas/celerybeat-schedule  --logfile=/var/log/boas/celerybeat.log  -l info &
# *** worker ***
# nohup celery worker -f /var/log/boas/boas_celery.log -l INFO &

CELERYD_TASK_TIME_LIMIT

BROKER_TRANSPORT_OPTIONS

使用需要十分谨慎， 如果CELERYD_TASK_TIME_LIMIT设置的过小，会导致task还没有执行完，worker就被杀死;BROKER_TRANSPORT_OPTIONS 设置的过小，task有可能被多次反复执行。
"""