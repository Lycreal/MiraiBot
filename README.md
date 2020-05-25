MiraiBot
-------------
A qq bot for personal use.

### 简介

基于 [mirai](https://github.com/mamoe/mirai) 内核和 [python-mirai](https://github.com/NatriumLab/python-mirai) 接口的QQ机器人。

### 功能

在 [插件列表](plugins) 中查看对应的插件。

### 部署

在部署本项目之前需先部署一个提供 `mirai-api-http` 服务的无头客户端，可参考 [python-mirai文档](https://mirai-py.originpages.com/mirai/use-console.html) 。

```shell script
git clone https://github.com/Lycreal/mirai_bot
cd mirai_bot

cp bot_example.env bot.env
vim bot.env  # 修改qq号，authKey，以及其他环境变量
vim docker-compose.yml  # 修改端口，路径等

docker-compose up -d --build
```

## License
[MIT LICENSE](LICENSE)
