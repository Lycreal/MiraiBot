import os.path

__all__ = [
    'data_path',
    'setu_apikey', 'setu_proxy', 'setu_r18', 'setu_maximum'
]

data_path = os.path.join(os.path.dirname(__file__), 'data')

# 在根目录下创建 config_private.py , 写入以下内容并按需修改
# ============= START =============

setu_apikey: str = ''
setu_r18: str = '0'
setu_proxy: str = 'disable'
setu_maximum: int = 3

# ============== END ==============

try:
    from config_private import *
except ImportError:
    pass
