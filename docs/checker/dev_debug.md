# 第一个检查器

Lyrebird支持灵活的检查器编写、调试和运行。

## 环境准备

安装Lyrebird

```sh
pip3 install lyrebird
```

在检查器的默认路径~/.lyrebird/checkers/下，新建一个检查器。

## 编写检查器

第一个检查器的目的是实时检查Lyrebird的flow频道中图片数据的大小。

### 监听频道

在[消息总线](/advance/eventbus.md)的频道中，flow频道包含了所有的网络请求，监听flow频道以获得设备的网络请求。

```py
from lyrebird import CustomEventReceiver

event = CustomEventReceiver()

# 使用装饰器监听flow频道，当flow频道中出现新数据时，会回调img_size方法
@event('flow')
def img_size(msg):
    pass
```

### 数据校验

flow频道中出现新的数据时会回调检查器中的方法，并传入频道中的消息，此时可对该消息进行校验。

```py
from lyrebird import CustomEventReceiver

event = CustomEventReceiver()

# 检测阈值
THRESHOLD_IMG_SIZE = 1024

@event('flow')
def img_size(msg):
    if msg['flow']['size'] > THRESHOLD_IMG_SIZE:
        # 检测到数据中的size不满足预期值

    return
```

### 报警

当检测到不满足预期的数据时，可调用Lyrebird[消息总线](/advance/eventbus.md)的issue接口触发报警。

```py
from lyrebird import CustomEventReceiver

event = CustomEventReceiver()

THRESHOLD_IMG_SIZE = 1024

@event('flow')
def img_size(msg):
    if msg['flow']['size'] > THRESHOLD_IMG_SIZE:
        event.issue('Image size is beyond expectations!')

    return
```

## 调试

Lyrebird支持检查器的调试，调试时配置启动参数，使用--script命令指定启动时加载的脚本。

```sh
lyrebird --script [filename]
```

以VSCode为例，检查器debug配置如下。

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "checker",
            "type": "pythonExperimental",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/lyrebird",
            "args": [
                "--script",
                "${file}"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### 开始调试

在所调试脚本为打开窗口时，在调试窗口选择checker，点击开始按钮即可开始调试。

![](../img/checker-c.png)


至此，第一个检查器就编写完成了，启动Lyrebird，体验检查器功能吧！Have fun！
