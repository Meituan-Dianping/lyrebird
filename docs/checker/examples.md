# 示例

检查器中可以监听Lyrebird中的所有网络请求，也可监听消息总线中的其他事件，对其中需要校验的目标数据进行检测。

目前，lyrebird中提供了如下的示例脚本：

| Filename | Channel | Description |
| :------- | :------ | :---------- |
| [img_size.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/img_size.py) | flow | 检查网络请求中图片大小是否超出限制 |
| [duplicate_requests.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/duplicate_requests.py) | flow | 检查在某段时间内是否有重复的网络请求 |

## 大图检测

在网络请求中，图片是一种高消耗资源的数据，移动设备无需加载过大的图片，需要对这类请求的数据进行校验。

监听flow频道，从server.response部分中的头部信息读取图片大小，当图片大小超过阈值500KB时发出alert事件。

校验策略：

*  忽略无关的请求数据
*  从获得的数据集中，获取检测所需的目标数据
*  对目标数据进行校验，得到校验结果

## 重复请求检测

在一组网络请求中，可能会出现重复请求同一个接口的情况。

监听flow频道，从client.request部分中读取url，当在一段时间内发现重复的请求时，则发出重复请求警告。

校验策略：
*  忽略无关的请求数据
*  从获得的数据集中，获取检测所需的目标数据
*  对目标数据进行校验，得到校验结果
*  更新验证集合

报警信息在通知中心展示。

![](../img/checker-b.gif)
