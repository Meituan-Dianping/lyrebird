# 命令行

> 在通过pip安装Lyrebird之后，可以直接使用lyrebird命令行启动。

## -h --help 

查看帮助

```bash
> lyrebird -h
usage: lyrebird [-h] [-V] [-v] [--mock MOCK] [--proxy PROXY] [--data DATA]
                [-b] [-c CONFIG] [--log LOG] [--script SCRIPT]
                [--plugin PLUGIN]
                {src,plugin} ...

positional arguments:
  {src,plugin}

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show lyrebird version
  -v                    Show verbose log
  --mock MOCK           Set mock server port, default port is 4272
  --proxy PROXY         Set proxy server port, default port is 9090
  --data DATA           Set data dir, default is "./data/"
  -b, --no_browser      Start without open a browser
  -c CONFIG, --config CONFIG
                        Start with a config file. Default is
                        "~/.lyrebird/conf.json"
  --log LOG             Set output log file path
  --script SCRIPT       Set a checker script path
  --plugin PLUGIN       Set a plugin project path
```

## -V --version 

查看版本

```bash
> lyrebird -V
Lyrebird 1.6.0
```

## -v -vvv 

显示详细日志

```bash
# lyrebird 将以静默模式启动
> lyrebird
# lyrebird 将以简单日志模式启动
> lyrebird -v
# lyrebird 将以详细日志模式启动
> lyrebird -vvv
```

## --mock 

指定mock服务端口

```bash
# 指定mock服务端口,lyrebird将在9000端口开启mock服务端口。(默认端口是9090)
> lyrebird --mock 9000
```

## --proxy 

指定代理服务端端口

```bash
# 指定代理服务的端口,lyrebird将在8080端口开启代理服务端口。(默认端口是4272)
> lyrebird --proxy 8080
```

## --data

```bash
# 指定mock数据根目录
> lyrebird --data ~/work/mockdata
```

## -b --no_browser

启动时不打开浏览器

## -c --config

使用指定配置文件启动lyrebird

## --log

指定输出日志文件的位置

## --script 

从指定路径加载[检查器](./checker.html)([Checker](./checker.html))脚本
用于调试检查器脚本

## --plugin 

从源码启动插件工程，用于插件开发和调试。

## gen

从模板生成一个插件项目

安装好Lyrebird后，可通过Lyrebird命令行工具生成插件

```
# 在指定路径创建插件工程
lyrebird gen /your/workspace/path

# 创建过程中会要求输入插件名（用作包名\显示名称\插件项目目录名）
>Please input your project name:

# 例如输入demo_project
# 您将会在 /your/workspace/path/demo_project得到一个插件工程
```
