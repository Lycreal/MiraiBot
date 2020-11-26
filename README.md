MiraiBot
-------------

### 简介

基于 [mirai](https://github.com/mamoe/mirai) 内核和 [python-mirai](https://github.com/NatriumLab/python-mirai) 接口的QQ机器人。

### 功能

- [使用说明](plugins/help)
- [色图](plugins/setu)
- [搜图](plugins/pic_finder)
- [撤回](plugins/revoke)
- [bilibili 动态监控](plugins/bili_dynamic)
- [bilibili 小程序解析](plugins/bili_extractor)
- [直播监控](plugins/live_monitor)
- [随机图片](plugins/random_picture)

### 部署

运行环境：python3.8+

0. 运行 [mirai-console](https://github.com/mamoe/mirai-console) 并安装 [mirai-api-http](https://github.com/mamoe/mirai-api-http) 插件。
1. `git clone --depth=1 https://github.com/Lycreal/MiraiBot && cd MiraiBot`
2. `pip3 install -r requirements.txt`
3. \[可选\] 在项目根目录创建文件 `config_private.py` 并编辑(详见 `config.py` )
4. `python3 run.py "mirai://localhost:8080/ws?authKey=<authKey>&qq=<qq号>"`

### 相关项目

- [mirai](https://github.com/mamoe/mirai)
- [mirai-console](https://github.com/mamoe/mirai-console)
- [mirai-api-http](https://github.com/mamoe/mirai-api-http)
- [python-mirai](https://github.com/NatriumLab/python-mirai) - [备份](https://github.com/Lycreal/python-mirai)

## License
[GNU AGPLv3](LICENSE)
