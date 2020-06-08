import os.path

__all__ = [
    'data_path',
    'setu_apikey', 'setu_proxy', 'setu_r18'
]

data_path = os.path.join(os.path.dirname(__file__), 'data')

setu_apikey: str = ''
setu_r18: str = '0'
setu_proxy: str = 'disable'

try:
    from config_private import *
except ImportError:
    pass
