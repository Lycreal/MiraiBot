import os.path

data_path = os.path.join(os.path.dirname(__file__), 'data')

setu_apikey: str = ''

try:
    from config_private import *
except ImportError:
    pass
