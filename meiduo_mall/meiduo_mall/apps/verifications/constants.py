# 定义子应用的常量，置于子应用而非项目中，降低耦合。

SMS_CODE_REDIS_EXPIRES = 300  # 短信验证码有效期,300s
SEND_SMS_CODE_INTERVAL = 60  # 短信在60s内是否发送过
