import os
from mirai import Mirai
from plugins import load_plugins, load_env

data_path = os.path.join(os.path.dirname(__file__), 'data')

if __name__ == '__main__':
    load_env('bot.env')
    params = {
        'host': os.environ.get('host', 'localhost'),
        'port': os.environ.get('port', 8080),
        'authKey': os.environ.get('authKey', ''),
        'qq': os.environ.get('qq', ''),
        'websocket': os.environ.get('websocket', True)
    }
    app = Mirai(**params)
    load_plugins(app)

    app.run()
