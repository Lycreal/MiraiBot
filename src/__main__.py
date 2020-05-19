import importlib
from pathlib import Path
from mirai.logger import Session
from .app import app


def load_plugins():
    plugin_dir = Path(__file__).parent
    module_prefix = plugin_dir.name

    for plugin in plugin_dir.iterdir():
        if plugin.is_dir() \
                and not plugin.name.startswith('_') \
                and plugin.joinpath('__init__.py').exists():
            load_plugin(f'{module_prefix}.{plugin.name}')


def load_plugin(module_path: str):
    try:
        importlib.import_module(module_path)
        Session.info(f'Succeeded to import "{module_path}"')
    except Exception as e:
        Session.error(f'Failed to import "{module_path}", error: {e}')
        Session.exception(e)


load_plugins()
app.run()
