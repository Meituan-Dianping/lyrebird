"""
checker example

steps:
- ignore unexepcted object
- prepare useful info
- check data
- update storage data

Info used in channel flow
├── name
├── time
└─┬ flow
  └─┬ request
    ├─┬ headers
    │ └── Content-Type
    ├── method
    └── url

"""


import time
import hashlib
from collections import OrderedDict
from lyrebird import event
from urllib.parse import urlparse, urlencode, parse_qsl


# THRESHOLD_TIME: Range of duplicate requests in seconds
THRESHOLD_TIME = 0.2

# HISTORY_URL: storage history checked url
HISTORY_URL = OrderedDict()

IGNORE_HOSTNAME = [
    'report.meituan.com',
    'frep.meituan.net'
]

IGNORE_PARAMETER = ['token',
                    'version_name',
                    'uuid'
                    ]


@event('flow')
def duplicate_request(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

    # 2.prepare useful info
    origin_url = msg['flow']['request']['url']
    sorted_url = sort_params(origin_url[origin_url.rfind('//')+2:])
    request_key_list = [
        sorted_url,
        msg['flow']['request']['method']
    ]
    request_key = get_md5_code(request_key_list)
    request_time = msg['time']

    # 3.check data
    if request_key in HISTORY_URL:

        history_request_time = HISTORY_URL[request_key]['time']
        if request_time - history_request_time < THRESHOLD_TIME:

            url = HISTORY_URL[request_key]['url']

            title = f'Duplicated requests: {url}\n'

            description = f'Duplicated requests: {url}\n'
            description += f'First at {history_request_time}\n'
            description += f'Second at {request_time}\n'

            event.issue(title, description)

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

def ignore_check(msg):
    if msg.get('name') != 'client.request':
        return True
    if urlparse(msg['flow']['request']['url']).hostname in IGNORE_HOSTNAME:
        return True
    return False

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
        md5_module.update(bytes(key, encoding = "utf8")  )
    return md5_module.hexdigest()
