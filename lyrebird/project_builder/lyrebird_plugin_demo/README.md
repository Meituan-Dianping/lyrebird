<h1 align="center">{{project_name}}</h1>

----

# 快速开始

## 环境要求

* macOS

* Python3.7及以上


## 安装


## 启动

```bash
lyrebird
```

## 使用


----

# 开发者指南

## 开发环境

* macOS OR Linux

* Python3

* NodeJS

* vscode(推荐)

* Chrome(推荐)

## 配置工程

```bash
# 进入工程目录
cd {{project_name}}

# 初始化后端开发环境
python3 -m venv --clear venv

# 初始化前端开发环境
cd frontend
npm install
cd -

# 使用IDE打开工程（推荐vscode）
code .
```

## 调试代码

### Vscode debug 配置
```JSON
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "backend",
            "type": "python",
            "request": "launch",
            "module": "lyrebird",
            "console": "integratedTerminal",
            "args": [
                "-vv",
                "--plugin",
                "${workspaceFolder}"
            ]
        },
        {
            "name": "frontend",
            "type": "chrome",
            "request": "launch",
            "url": "http://localhost:8080/ui/static/",
            "webRoot": "${workspaceFolder}/frontend/src/",
            "breakOnLoad": true,
            "sourceMapPathOverrides": {
              "webpack:///src/*": "${webRoot}/*"
            }
        }
    ]
}
```

### 后端代码

1. 激活python虚拟环境

    通过 ```source venv/bin/activate``` 来激活该环境

2. 通过Debug功能启动

    按照上面 debug配置中 python:Lyrebrid配置启动即可

### 前端代码

1. 启动node server

```bash
# 进入前端目录
cd frontend

# 启动前端node serve
npm run serve
```

2. 通过Debug功能启动浏览器

    按照上面 debug配置中 vuejs: chrome 配置启动即可

    > 注意: vscode 需要安装chrome debug插件
