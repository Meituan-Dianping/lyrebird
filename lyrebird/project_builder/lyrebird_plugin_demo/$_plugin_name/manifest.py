from lyrebird.plugins import manifest
from . import handler
from . import status


manifest(
    id='demo',
    name='Demo',
    api=[
        # http://localhost:9090/plugins/demo/api/list
        ('/api/list', handler.request_list, ['GET']),
        # http://localhost:9090/plugins/demo/api/mock
        ('/api/mock', handler.mock, ['POST']),
        # http://localhost:9090/plugins/demo/api/reset
        ('/api/reset', handler.reset, ['PUT'])
    ],
    background=[
    ],
    event=[
        ('flow', handler.on_request)
    ],
    status=[
        status.StatusbarDemoImage,
        status.StatusbarDemoText
    ]
)
