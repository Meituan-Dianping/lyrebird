# 使用指南

扩展(Extension)是一种支持用户⾃定义的Python脚本，在Lyrebird运行的过程中，于后台并行地工作。

无需搭建工程和前端开发，检查器可灵活、轻巧、便捷、准确的对[消息总线](/advance/eventbus.md)频道中的数据进行分析和校验。

Extension默认支持三种类型：
1. 请求修改器(Modifier): 如为请求添加Header Key、[修改请求的Param](/checker/request_editor.html#修改请求)等
2. 请求检查器(Checker): 如可通过检查器监听网络请求频道，检测网络请求中的[图片大小](/checker/examples.html#大图检测)是否满足预期，或检测是否[重复请求](/checker/examples.html#重复请求检测)了同一个接口等
3. 其他(Other): 未分类或者综合应用

可在脚本中使用全局变量**ExtensionCategory**(String类型)人为指定Extension类型

可以在Lyrebird运行过程中随时开启或关闭检查器，即插即用，方便灵活。

![](../img/checker-a.png)

> 展开Extension标签可查看当前运行的扩展，按组别聚合。
> Activated Tab展示已激活的Extension, Deactivated Tab展示未激活的Extension

如果需要高级的检查和展示，可使用[插件](/plugins/)开发实现更复杂的场景和功能。

## 载入检查器

运行时携带的检查器存放在默认路径~/.lyrebird/checkers下。对检查器的新增、修改、删除检查器，可在默认目录下操作文件。

当默认目录中没有可用的检查器时，会自动载入示例脚本。目前提供的示例脚本如下：

| Filename | Type | Description |
| :------- | :------- | :------- |
| [img_size.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/img_size.py) | 检查器 | 检查网络请求中图片大小是否超出限制 |
| [duplicate_requests.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/duplicate_requests.py) | 检查器| 检查在某段时间内是否有重复的网络请求 |
| [add_request_param.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/add_request_param.py) | 修改器 | 在Request中添加Param |
| [add_response_header.py](https://github.com/Meituan-Dianping/lyrebird/tree/master/lyrebird/examples/checkers/add_response_header.py) | 修改器 | 在Response中添加Header Key |

此外，Lyrebird支持使用在启动时指定需要加载的脚本。

```sh
lyrebird --script [filename] --script [filename]
```

## 捕获报警

在获取到数据后，便可对该数据进行检验和处理。当发现异常数据时，Lyrebird会在通知中心展示报警信息。

![](../img/checker-b.gif)

报警中可携带检查出的异常信息，也可以携带[消息总线](/advance/eventbus.md)中其它频道的消息作为辅助信息，以丰富报警信息。
