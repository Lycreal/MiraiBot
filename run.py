import sys
from mirai import Mirai
from plugins import load_plugins

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        app = Mirai(sys.argv[1])
        load_plugins(app)
        app.run()
    else:
        print('\n'.join([line.strip() for line in f"""
        Usage: python3 {sys.argv[0]} mirai://localhost:8080/ws?authKey=$authKey&qq=$qq

        Visit https://mirai-py.originpages.com/tutorial/hello-world.html#hello-world-2 for more details.
        """.strip().splitlines()]))
        exit(1)
