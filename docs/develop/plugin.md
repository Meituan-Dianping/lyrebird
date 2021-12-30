# 自定义插件开发

## 创建项目

安装好Lyrebird后，可通过Lyrebird命令行工具生成自定义插件

```
# 在指定路径创建插件工程
lyrebird gen /your/workspace/path

# 创建过程中会要求输入插件名（用作包名\显示名称\插件项目目录名）
>Please input your project name:

# 例如输入demo_project
# 您将会在 /your/workspace/path/demo_project得到一个插件工程
```



## 结构说明

工程结构如下：
```
.
├── MANIFEST.in
├── README.md
├── frontend
│   ├── README.md
│   ├── babel.config.js
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   │   ├── favicon.ico
│   │   └── index.html
│   ├── src
│   │   ├── App.vue
│   │   ├── apis
│   │   │   └── index.js
│   │   ├── assets
│   │   │   └── logo.png
│   │   ├── components
│   │   │   └── HelloWorld.vue
│   │   ├── main.js
│   │   └── store
│   │       └── index.js
│   └── vue.config.js
├── plugin_demo
│   ├── __init__.py
│   ├── handler.py
│   ├── manifest.py
│   └── version.py
├── requirements.txt
└── setup.py

```

## 构建项目

插件工程分前端和插件本身两部分。 构建时需要**依次**构建前端、插件本身

### 构建前端

前端工程存储于frontend目录下

```
cd frontend
npm install
npm run build
cd -
```

### 构建插件

```
python3 setup.py sdist
```

## 开发调试

### 前端

```
cd frontend
npm run serve
```

推荐使用[VUE devtools](https://github.com/vuejs/vue-devtools)



### 插件

```
# 在项目目录下通过Lyrebird拉起插件
lyrebird --plugin .
```

以VSCODE为例，添加下面的启动方式即可开始调试
```JSON
{
    "name": "Debug",
    "type": "python",
    "request": "launch",
    "module": "lyrebird",
    "args": [
        "-b",
        "-v",
        "--plugin", 
        "${workspaceFolder}"
    ]
}
```
