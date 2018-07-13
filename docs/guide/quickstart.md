# 快速开始

## 环境要求

* macOS

* Python3.6及以上

## 安装

```bash
# 安装python3
brew install python3
```

```python        
pip3 install lyrebird
```
        
## 启动

```python
lyrebird
```

## 连接移动设备

* 启动Lyrebird后，移动设备需要通过代理的方式将请求数据接入。                

* 将移动设备的代理地址设为当前电脑地址，默认端口为4272（IP地址可查看Lyrebird启动时输出的日志）

* 被测设备上用浏览器打开 http://mitm.it, 选择对应操作系统安装证书

> 现在，可以开始操作移动设备了。Lyrebird将显示捕获到的http请求。

## 查看及录制数据

<img src="../img/Inspector-with-tag.png" style="width: 800px">

* 如上图，准备工作完成后，操作手机即可以看到HTTP请求的数据。

* 上图中按钮栏的按钮依次是：

    1. 录制按钮
    2. 清除inspector数据按钮
    3. 新建mock数据组按钮
    4. 激活mock数据组选择器
    5. 取消激活mock数据按钮

* 操作图中(1)按钮栏的录制按钮，则可开始数据的录制工作。

    > 录制数据要求新建或选中一组mock数据。即操作按钮3或4。

* 按钮4 - 激活mock数据选择器，选择mock数据后。经过Lyrebird的请求会被mock，如果mock数据中没有匹配的数据，则会代理该请求。

    > mock数据可由左边导航栏切换到DataManager界面进行编辑管理