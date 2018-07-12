import lyrebird
from flask import request


class MyUI(lyrebird.PluginView):

    def index(self):
        """
        插件首页(必选)

        如果不需要jinja模板渲染，可使用send_template_file
        self.send_template_file('index.html')
        """
        return self.render_template('index.html')

    def update_data(self):
        """
        post请求        
        """
        return f'From /api/post got form name:{request.form.get("name")}'

    def get_data(self, name=''):
        """
        get请求
        """
        return f'From /api/get/ got name {name}'

    def on_data_update(self, data):
        print('Data update', data)

    def on_create(self):
        """
        插件初始化函数（必选）
        """
        # 设置模板目录（可选，设置模板文件目录。默认值templates）
        self.set_template_root('lyrebird_demo')
        # 设置静态文件目录（可选，设置静态文件目录。默认值static）
        self.set_static_root('lyrebird_demo')
        # 添加一个POST请求的接口(可选)
        self.add_url_rule('/api/post', view_func=self.update_data, methods=['POST'])
        # 添加一个Get请求的接口(可选)
        self.add_url_rule('/api/get/<string:name>', view_func=self.get_data)
        # 设置socketio处理接口(可选)
        self.on_event('from-UI', self.on_data_update, namespace='/demo')
