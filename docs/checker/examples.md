# 示例

检查器可以监听Lyrebird[消息总线](/advance/eventbus.md)中的任意频道，对其中需要校验的目标数据进行检测。

目前，Lyrebird中提供了如下的示例脚本：

| Filename | Channel | Description |
| :------- | :------ | :---------- |
| [img_size.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/img_size.py) | flow | 检查网络请求中图片大小是否超出限制 |
| [duplicate_requests.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/duplicate_requests.py) | flow | 检查在某段时间内是否有重复的网络请求 |

## 大图检测

在网络请求中，图片是一种高消耗资源的数据，移动设备无需加载过大的图片，因此需要对这类请求的数据进行校验。

检查的思路为，监听flow频道，从server.response部分中的头部信息读取图片大小，当图片大小超过阈值500KB时发出报警。

### 忽略无关数据

仅关注server.response部分的数据，且Content-Type为image的数据。

```py
from lyrebird import CustomEventReceiver

event = CustomEventReceiver()

THRESHOLD_IMG_SIZE = 500

@event('flow')
def img_size(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

def ignore_check(msg):
    if msg['name'] != 'server.response':
        return True
    if 'response' not in msg['flow']:
        return True
    if 'image' not in msg['flow']['response']['headers']['Content-Type']:
        return True
    return False

```

### 获取目标数据

从获得的数据集中，获取检测所需的目标数据:
*  size: 图片大小

```py
from decimal import Decimal
...

@event('flow')
def img_size(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

    # 2.prepare useful info
    img_size = int(msg['flow']['size'])
    img_size = Decimal(img_size / 1024).quantize(Decimal('0.0'))
```

### 得出校验结果

对目标数据进行校验，当图片大小超过500KB时，发出大图报警。

```py
...

@event('flow')
def img_size(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

    # 2.prepare useful info
    img_size = int(msg['flow']['size'])
    img_size = Decimal(img_size / 1024).quantize(Decimal('0.0'))

    # 3.check data
    if img_size > THRESHOLD_IMG_SIZE:
        img_url = msg['flow']['request']['url']
        event.issue(f'Image size {img_size}KB is beyond expectations: {img_url}\n')
```

## 重复请求检测

在一组网络请求中，可能会出现重复请求同一个接口的情况。

检查的思路为，监听flow频道，从client.request部分中读取URL，当在200毫秒内发现重复的请求时，则发出重复请求报警。

### 忽略无关数据

仅关注client.request部分的数据，且过滤掉不关注的域名。

```py
from lyrebird import CustomEventReceiver
from urllib.parse import urlparse

event = CustomEventReceiver()

IGNORE_HOSTNAME = [
    'report.meituan.com',
    'frep.meituan.net'
]

@event('flow')
def duplicate_request(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

def ignore_check(msg):
    if msg.get('name') != 'client.request':
        return True
    if urlparse(msg['flow']['request']['url']).hostname in IGNORE_HOSTNAME:
        return True
    return False
```

### 获取目标数据

获取校验所需的数据：
*  url：请求的标示，判断是否有重复请求的重要依据。需要过滤掉请求中不关注的参数，并使参数有序排列
*  method： 请求方法
*  request_key：由处理后的url和method生成的串，作为请求的唯一标示
*  time：请求发出的时间

```py
import hashlib
from urllib.parse import urlparse, urlencode, parse_qsl

IGNORE_PARAMETER = ['token',
                    'version_name',
                    'uuid'
                    ]

@event('flow')
def duplicate_request(msg):
    ...

    # 2.prepare useful info
    origin_url = msg['flow']['request']['url']
    sorted_url = sort_params(origin_url[origin_url.rfind('//')+2:])
    request_key_list = [
        sorted_url,
        msg['flow']['request']['method']
    ]
    request_key = get_md5_code(request_key_list)
    request_time = msg['time']

def sort_params(url):
    # serialize parameters and remove ignored parameters
    if len(urlparse(url).query):
        origin_parameters = parse_qsl(urlparse(url).query)
        origin_parameters = [param for param in origin_parameters if param[0] not in IGNORE_PARAMETER]
        origin_parameters.sort(key=lambda x:x[0])
        return url.split('?')[0] + '?' + urlencode(origin_parameters)
    else:
        return url

def get_md5_code(keys:list):
    md5_module = hashlib.sha224()
    for key in keys:
        md5_module.update(bytes(key, encoding = "utf8"))
    return md5_module.hexdigest()
```
### 得到校验结果

维护一个记录所有历史请求的存储器，若当前请求存在于历史请求中，且两次请求的时间间隔小于200ms，则界定为一次重复请求。

```py
import time
from collections import OrderedDict

THRESHOLD_TIME = 0.2

HISTORY_URL = OrderedDict()

@event('flow')
def duplicate_request(msg):
    ...

    # 3.check data
    if request_key in HISTORY_URL:
        if request_time - HISTORY_URL[request_key]['time'] >= THRESHOLD_TIME:
            return

        url = HISTORY_URL[request_key]['url']
        event.issue(f'Duplicate request: {url}')
```

### 更新验证集合

维护历史请求数据，将新的请求数据存入历史请求，并删除其中的过期数据。

```py
...

@event('flow')
def duplicate_request(msg):
    ...

    # 4.update storage data
    HISTORY_URL.update({
        request_key: {
            'time': request_time,
            'url': sorted_url
        }
    })

    overdue_urls = []
    for key, value in HISTORY_URL.items():
        if time.time() - value['time'] >= THRESHOLD_TIME:
            overdue_urls.append(key)
        else:
            break
    for overdue_url in overdue_urls:
        del HISTORY_URL[overdue_url]
```
