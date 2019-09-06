# 接口

接口根目录为 /api    

比如请求状态的接口，实际路径为 /api/status

## Lyrebird状态

**/status**

```bash
> curl http://localhost:9090/api/status
{
    "code":1000,
    "ip":"192.168.1.10",
    "message":"success",
    "mock.port":9090,
    "proxy.port":4272,
    "version":"1.7.0"
}
```

## 获取缓存中请求列表

**/flow**

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

## 获取缓存中请求详情

**/flow/{flowID}**

```bash
> curl http://localhost:9090/api/flow/0379d5bd-a5be-4e55-8a61-0a79f7fd558e
{
    "code":1000,
    "data":{
        "client_address":"127.0.0.1",
        "duration":0.028654098510742188,
        "id":"0379d5bd-a5be-4e55-8a61-0a79f7fd558e",
        "request":{
            "headers":{
                "Accept":"*/*",
                "Host":"localhost:9090",
                "User-Agent":"curl/7.54.0"
                },
            "host":"localhost",
            "method":"GET",
            "path":"/anything/xkepiIBS",
            "port":"80",
            "query":{},
            "scheme":"http",
            "timestamp":1567656334.366,
            "url":"http://localhost/anything/xkepiIBS"
        },
        "response":{
            "code":200,
            "data":"{\"args\": {}, \"data\": \"\", \"files\": {}, \"form\": {}, \"headers\": {\"Accept\": \"*/*\", \"Accept-Encoding\": \"gzip, deflate\", \"Connection\": \"keep-alive\", \"Host\": \"localhost\", \"User-Agent\": \"curl/7.54.0\"}, \"json\": null, \"method\": \"GET\", \"origin\": \"172.17.0.1\", \"url\": \"http://localhost/anything/xkepiIBS\"}",
            "headers":{
                "Access-Control-Allow-Credentials":"true",
                "Access-Control-Allow-Origin":"*","Connection":"keep-alive",
                "Content-Length":"350",
                "Content-Type":"application/json",
                "Date":"Thu, 05 Sep 2019 04:05:34 GMT",
                "Server":"gunicorn/19.9.0",
                "lyrebird":"proxy"
            },
            "timestamp":1567656334.395
        },
        "size":350,
        "start_time":1567656334.365847
    },
    "message":"success"
}
```

## 激活mock数据组 

**/mock/{string:group_id}/activatie**

```bash
> curl -X PUT http://localhost:9090/api/mock/5a73de9c-cfae-4535-abfd-bb220d2239c4/acticate
{
    "code": 1000,
    "message": "success"
}
```

## 取消激活mock数据

**/mock/group/deactivate**

```bash
> curl -X PUT http://localhost:9090/api/mock/group/deacticate
{
    "code": 1000,
    "message": "success"
}
```

## 获取已激活mock数据

**/mock/activated**

查询已激活的group
```bash
> curl http://localhost:9090/api/mock/activated
{
    "code":1000,
    "message":"success",
    "data": {
        "5a73de9c-cfae-4535-abfd-bb220d2239c4":{
            "id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
            "name":"MyMockDataGroupA",
            "parent_id":"988f2d7c-7447-41d8-a645-d8ae8d43d046",
            "super_id":null,
            "type":"group"
            "children": [
                {
                    "id":"795ef3f0-b0b4-4a62-8ae1-65d0573a377f",
                    "name":"/anything/DYoaLRmx",
                    "parent_id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
                    "type":"data"
                },
                {
                    "id":"51f9c500-7de4-4d33-b2fb-3ac083e75b05",
                    "name":"/anything/MGOdQgqR",
                    "parent_id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
                    "type":"data"
                },
                {
                    "id":"9e7586b5-cb0e-4190-8fdf-275b030fd0a0",
                    "name":"/anything/MOSjHNtJ",
                    "parent_id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
                    "type":"data"
                },
                {
                    "id":"8ecd5bac-c1b1-4ec7-8604-56c89dc2d9d3",
                    "name":"/anything/xkepiIBS",
                    "parent_id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
                    "type":"data"
                },
                {
                    "id":"004905ee-2e00-431f-b233-f520753c0698",
                    "name":"/anything/zPmSkEsj",
                    "parent_id":"5a73de9c-cfae-4535-abfd-bb220d2239c4",
                    "type":"data"
                }
            ]
        }
    }
}
```

## 获取指定频道的消息总线数据

**/event/{channel...}**

```bash
> curl http://localhost:9090/api/event/flow+notice
{
    "code": 1000,
    "events": [
        {
            "channel": "flow",
            "content": "{\"flow\": {\"id\": \"0379d5bd-a5be-4e55-8a61-0a79f7fd558e\", \"size\": 350, \"duration\": 0.028654098510742188, \"start_time\": 1567656334.365847, \"client_address\": \"127.0.0.1\", \"request\": {\"headers\": {\"Host\": \"localhost:9090\", \"User-Agent\": \"curl/7.54.0\", \"Accept\": \"*/*\"}, \"method\": \"GET\", \"query\": {}, \"timestamp\": 1567656334.366, \"url\": \"http://localhost/anything/xkepiIBS\", \"scheme\": \"http\", \"host\": \"localhost\", \"port\": \"80\", \"path\": \"/anything/xkepiIBS\"}, \"response\": {\"code\": 200, \"headers\": {\"lyrebird\": \"proxy\", \"Server\": \"gunicorn/19.9.0\", \"Date\": \"Thu, 05 Sep 2019 04:05:34 GMT\", \"Connection\": \"keep-alive\", \"Content-Type\": \"application/json\", \"Content-Length\": \"350\", \"Access-Control-Allow-Origin\": \"*\", \"Access-Control-Allow-Credentials\": \"true\"}, \"timestamp\": 1567656334.395, \"data\": {\"args\": {}, \"data\": \"\", \"files\": {}, \"form\": {}, \"headers\": {\"Accept\": \"*/*\", \"Accept-Encoding\": \"gzip, deflate\", \"Connection\": \"keep-alive\", \"Host\": \"localhost\", \"User-Agent\": \"curl/7.54.0\"}, \"json\": null, \"method\": \"GET\", \"origin\": \"172.17.0.1\", \"url\": \"http://localhost/anything/xkepiIBS\"}}}, \"message\": \"URL: http://localhost/anything/xkepiIBS\\nMethod: GET\\nStatusCode: 200\\nDuration: 29ms\\nSize: 350.0 B\", \"channel\": \"flow\", \"id\": \"43844a6d-8f79-4ec9-8c1a-9491a5b697e3\", \"timestamp\": 1567656334.396, \"sender\": {\"file\": \"api_mock.py\", \"function\": \"index\"}}",
            "event_id": "43844a6d-8f79-4ec9-8c1a-9491a5b697e3",
            "id": 11520,
            "timestamp": 1567656334.411214
        }
    ],
    "message": "success",
    "page": 0,
    "page_count": 346,
    "page_size": 20
}
```
