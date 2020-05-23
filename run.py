import os
from mirai import Mirai
from plugins import load_plugins

params = {
    'host': os.environ.get('host', 'localhost'),
    'port': os.environ.get('port', 8080),
    'authKey': os.environ.get('authKey', '0'),
    'qq': os.environ.get('qq', '0'),
    'websocket': True
}

app = Mirai(**params)
load_plugins(app)
app.run()
