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
git clone https://github.com/Lycreal/mirai_bot && cd mirai_bot
cp .example.env .env
vim .env
cp bot.example.env bot.env
vim bot.env
docker-compose up -d
```

## License
[MIT LICENSE](LICENSE)
