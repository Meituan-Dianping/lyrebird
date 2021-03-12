## Checker Examples

| Filename | Description |
| :------- | :---------- |
| duplicate_requests.py | 检查在某段时间内是否有重复的网络请求 |
| img_size.py | 检查图片大小是否超出限制 |
| add_request_param.py | 修改请求参数 |
| add_response_header.py | 修改请求返回数据 |

## Debug Config
调试检查器的Vscode debug配置如下
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
