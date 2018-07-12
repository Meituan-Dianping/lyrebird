from lyrebird import HandlerContext
from flask import Response


class MyDataHandler:

    def handle(self, handler_context: HandlerContext):
        if 'www.baidu.com' in handler_context.request.path:
            print('Got "baidu" in request url')
            if handler_context.response:
                origin_data = handler_context.response.get_data().decode()
                new_data = origin_data.replace('百度', 'google')
                new_data = new_data.replace('<img hidefocus="true" src="//www.baidu.com/img/bd_logo1.png" width="270" height="129">',
                                            '<div><h1>Google</h1></div>')
                handler_context.response.set_data(new_data.encode())
        elif 'meituan' in handler_context.request.path:
            print('Got "meituan" in request url')
            handler_context.response = Response('Hello', 404)
        else:
            print(f'Got url {handler_context.request.url[:100]}')
