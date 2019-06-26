# 接口

接口根目录为 /api    

比如请求状态的接口，实际路径为 /api/status

## /status

获取Lyrebird状态

```bash
> curl http://localhost:9090/api/status
{
    "code":1000,
    "ip":"192.168.1.10",
    "message":"success",
    "mock.port":9090,
    "proxy.port":4272,
    "version":"1.6.0"
}
```

## /flow

获取当前flow列表

```bash
> curl http://localhost:9090/api/flow
[
    {
        "id": "c78e760b-f475-4d69-97f1-333ea0ab61bd", 
        "size": 2381, 
        "duration": 0.14836382865905762, 
        "start_time": 1553589544.255983, 
        "request": {
            "url": "http://www.baidu.com", 
            "path": "", 
            "host": "www.baidu.com", 
            "method": "GET"
            }, 
        "response": {
            "code": 200, 
            "mock": "proxy"
            }
    }, 
    {
        "id": "b7384bbb-abf8-4f6b-a4c3-c8685c926c1c", 
        "size": 2381, 
        "duration": 0.13956403732299805, 
        "start_time": 1553589541.328183, 
        "request": {
            "url": "http://www.baidu.com", 
            "path": "", 
            "host": "www.baidu.com", 
            "method": "GET"
            }, 
        "response": {
            "code": 200, 
            "mock": "proxy"
            }
    }
]
```

## /mock/{string:group_id}/activatie

通过group-id激活mock数据

## /mock/activated

查询已激活的group


## /group

获取数据关系树

## /group/<string:group_id>

获取指定节点下的数据关系树

## /data/<string:data_id>

获取数据详情

## /cut/<string:_id>

剪切指定ID的数据到剪切板

## /copy/<string:_id>

复制指定ID的数据到剪切板

## /paste/<string:_id>

从数据剪切板粘贴数据到指定ID的节点下

## /conflict/id/<string:group_id>

检查指定组过滤条件冲突情况

## /conflict/activated

检查已激活数据过滤条件冲突情况
