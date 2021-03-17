# 修改器

Lyrebird支持对请求进行修改的检查器，也称为[修改器](/checker/request_editor.md)、[请求修改器](/checker/request_editor.md)，支持的修改请求时机如下：

- 客户端发起请求后，mock和代理动作前。使用`@on_request`。

- 获得响应数据后，返回给客户端前。使用`@on_response`。


## 环境准备

请求修改器的环境准备与[检查器-环境准备](/checker/dev_debug.md#环境准备)相同。

## 编写

下面的例子中，将实现包含如下功能的修改器：

- 在请求request的url中，加入一个参数

- 在响应response的headers中，增加一个header


### 注册

将修改请求的方法注册至Lyrebird。

```python
from lyrebird import on_request

# 使用装饰器on_request，当新的请求进入Lyrebird时，会调用add_request_param方法
@on_request()
def add_request_param(flow):
    pass
```

当请求被Lyrebird代理时，会自动调用修改请求的方法，传入的内容结构如下。

```JSON
{
    "size": 4652,
    "duration": 0.28295302391052246,
    "start_time": 1615293597.4765,
    "request": {
        "headers": {
            // ...
        },
        "method": "GET",
        "timestamp": 1615293597.477,
        "url": "https://www.meituan.com",
    },
    "response": {
        "code": 200,
        "headers": {
            // ...
        },
        "data": ...
    }
}

```

注册回调时，支持指定过滤器rules，用于申明需要修改的请求具备的特征，能够更精准的进行请求修改。rules采用字典类型，其中：

- key为JSONPath，用于描述目标字符的位置

- value为正则表达式，用于匹配目标字符

```python
from lyrebird import on_request

# 此处使用rules申明目标请求的特征为：请求的request.url中包含poi/detail
@on_request(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_request_param(flow):
    pass
```

rules非必须指定的内容，当不传入rules时，默认修改全部请求。


### 修改请求

根据实际的需求进行请求修改。

```python
from lyrebird import on_request

@on_request(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_request_param(flow):
    # 直接修改flow中的内容
    if '?' in flow['request']['url']:
        flow['request']['url'] += '&param=1'
    else:
        flow['request']['url'] += '?param=1'
    # 请求修改完成后，无需返回任何内容
```

此时，我们已经使用`@on_request`实现了在请求request的url中加入参数。

接下来使用`@on_response`在响应response的headers中加入标示，`@on_response`的使用方法与`@on_request`相同，实现后的修改器如下。

```python
from lyrebird import on_request
# 引入on_response
from lyrebird import on_response

@on_request(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_request_param(flow):
    if '?' in flow['request']['url']:
        flow['request']['url'] += '&param=1'
    else:
        flow['request']['url'] += '?param=1'

@on_response(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_tag_in_response_headers(flow):
    # 在response headers中增加Mock-Tag
    flow['response']['headers']['Mock-Tag'] = 'Lyrebird'
```

## 调试

请求修改器的调试与[检查器-调试](/checker/dev_debug.md#调试)相同。

****

至此，我们共同完成了一个修改器的编写，期待和你一起共探索更多Lyrebird的功能！
