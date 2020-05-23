import importlib
from pathlib import Path
from mirai.logger import Session
from mirai import Mirai


def load_plugins(app: Mirai):
    plugin_dir = Path(__file__).parent
    module_prefix = plugin_dir.name

    for plugin in plugin_dir.iterdir():
        if plugin.is_dir() \
                and not plugin.name.startswith('_') \
                and plugin.joinpath('__init__.py').exists():
            load_plugin(app, f'{module_prefix}.{plugin.name}')


def load_plugin(app: Mirai, module_path: str):
    try:
        module = importlib.import_module(module_path)
        app.include_others(module.sub_app)
        Session.info(f'Succeeded to import "{module_path}"')
    except Exception as e:
        Session.error(f'Failed to import "{module_path}", error: {e}')
        Session.exception(e)
