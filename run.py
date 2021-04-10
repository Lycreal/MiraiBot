import sys
from mirai import Mirai
from plugins import load_plugins

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        app = Mirai(sys.argv[1])
        load_plugins(app)
        app.run()
    else:
        print(f'Usage: python3 {sys.argv[0]} mirai://localhost:8080/ws?authKey=$authKey&qq=$qq\n\n'
              'Visit https://natriumlab.github.io/tutorial/hello-world.html#hello-world-2 for more details.')
        exit(1)
