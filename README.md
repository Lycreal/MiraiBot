MiraiBot
-------------
A qq bot for personal use.

### 简介

基于 [mirai](https://github.com/mamoe/mirai) 内核和 [python-mirai](https://github.com/NatriumLab/python-mirai) 接口的QQ机器人。

### 功能

在 [插件列表](plugins) 中查看对应的插件。

### 部署

在部署本项目之前需先下载 [mirai-console](https://github.com/mamoe/mirai-console) 并安装 [mirai-api-http](https://github.com/mamoe/mirai-api-http) 插件。

```shell script
cp bot.example.env bot.env
vim bot.env

python3 run.py mirai://localhost:8080/ws?authKey=$authKey&qq=$qq
```

或

```shell script
docker build . -t mirai_bot

docker run -it --rm \
    -v ./data:/app/data \
#   -e setu_apikey=123456 \
    mirai_bot mirai://localhost:8080/ws?authKey=$authKey&qq=$qq
```

## License
[LICENSE](LICENSE)
