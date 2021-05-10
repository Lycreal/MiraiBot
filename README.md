MiraiBot
-------------
<a href="https://www.python.org" alt="python"><img src="https://img.shields.io/badge/python-3.8+-blue" /></a>
            
### 简介

基于 [mirai](https://github.com/mamoe/mirai) 内核和 [python-mirai](https://github.com/GreyElaina/python-mirai) 接口的QQ机器人。

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
(建议在虚拟环境中运行python)

0. 运行 [mirai-console](https://github.com/mamoe/mirai-console) 并安装 [mirai-api-http](https://github.com/mamoe/mirai-api-http) 插件。
1. `git clone https://github.com/Lycreal/MiraiBot && cd MiraiBot`
2. `pip3 install -r requirements.txt`
3. \[可选\] 在项目根目录创建文件 `config_private.py` 并编辑(详见 `config.py` )
4. `python3 run.py "mirai://localhost:8080/ws?authKey=<authKey>&qq=<qq号>"`

### 经过测试的运行环境
[bugfix-2021](https://github.com/Lycreal/python-mirai/tree/bugfix-2021)
```plain
mirai-core-all-2.5.0
mirai-console-2.5.0
mirai-console-terminal-2.5.0
mirai-api-http-v1.10.0
```
[kuriyama==0.3.6](https://github.com/Lycreal/python-mirai/tree/master)
```plain
mirai-core-1.0.2
mirai-core-qqandroid-1.1.3
mirai-console-0.5.2
mirai-api-http-v1.7.2
```
### 相关项目

- [mirai](https://github.com/mamoe/mirai)
- [mirai-console](https://github.com/mamoe/mirai-console)
- [mirai-api-http](https://github.com/mamoe/mirai-api-http)
- [python-mirai](https://github.com/GreyElaina/python-mirai)

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FLycreal%2FMiraiBot.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FLycreal%2FMiraiBot?ref=badge_shield)

[GNU AGPLv3](LICENSE)


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FLycreal%2FMiraiBot.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FLycreal%2FMiraiBot?ref=badge_large)