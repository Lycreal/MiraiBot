MiraiBot
-------------
A qq bot for personal use.

### 简介

基于 [mirai](https://github.com/mamoe/mirai) 内核和 [python-mirai](https://github.com/NatriumLab/python-mirai) 接口的QQ机器人。

### 功能

在 [插件列表](plugins) 中查看对应的插件。

### 部署

0. 运行 [mirai-console](https://github.com/mamoe/mirai-console) 并安装 [mirai-api-http](https://github.com/mamoe/mirai-api-http) 插件。
1. `git clone --depth=1 https://github.com/Lycreal/mirai_bot`
2. \[可选\] 在项目根目录创建文件 `config_private.py` 并编辑(参考 `config.py` )
3. `python3 run.py mirai://localhost:8080/ws?authKey=$authKey&qq=$qq`

## License
[GNU AGPLv3](LICENSE)
