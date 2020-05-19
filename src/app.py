import os
from mirai import Mirai

params = {
    'host': os.environ.get('host', 'localhost'),
    'port': os.environ.get('port', 8081),
    'authKey': os.environ.get('authKey', 'qwerty1234'),
    'qq': os.environ.get('qq', 123456),
    'websocket': True
}

app = Mirai(**params)
