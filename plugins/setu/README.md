色图
-------------

### 功能

发送色图。

### 使用方法

```plain
[<num>张][keyword]色图
num: 色图数量
keyword: 色图关键词
```

### 注意事项

本功能依赖 [随机色图](https://api.lolicon.app/#/setu) 提供的服务。

服务需要APIKEY，在 [此处](https://api.lolicon.app/#/setu?id=apikey) 申请。

> 允许不带 APIKEY，但调用额度很低，并且具有一定限制，仅供测试使用

若本机无法访问 pixiv 图片服务器，可将 `setu_proxy` 清空。

以下配置与 [请求](https://api.lolicon.app/#/setu?id=%e8%af%b7%e6%b1%82) 一节中的 `apikey`, `r18` , `proxy` 对应。

### 配置

```python
setu_apikey = ''
setu_r18 = ''
setu_proxy = 'disable'
```

### 鸣谢

[随机色图](https://api.lolicon.app/#/setu)
