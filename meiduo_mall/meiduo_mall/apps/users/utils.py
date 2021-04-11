

def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录视图的构造顺应数据函数，追加username,id"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }