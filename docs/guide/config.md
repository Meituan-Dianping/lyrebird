# 配置文件

Lyrebird第一次启动后，会在 ~/.lyrebird/conf.json 生成一个配置文件。

```json
{
    "version": "0.10.5",
    "proxy.filters": [],
    "proxy.port": 4272,
    "mock.port": 9090,
    "mock.data": "{{current_dir}}/mock_data/personal",
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }
}
```
## proxy.filters

**代理请求白名单**

不配置时所有请求都将从代理服务转发至mock服务端口。

配置后将只转发白名单内的请求到mock服务。其他请求将直接代理到原始地址，不做处理。

示例
只处理所有包含meituan或google字符串的请求
```json
{
    "proxy.filters":[
        "meituan",
        "google"
    ]
}
```


## proxy.port

代理服务端口。 默认值4272

## mock.port

mock服务端口。默认9090

## mock.data

mock数据根目录。
