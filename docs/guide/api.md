# 接口

接口根目录为 /api    

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

通过mock-group-id激活mock数据


