from lyrebird.plugins import manifest
from . import handler

manifest(
    id='demo',
    name='Demo',
    api=[
        # http://localhost:9090/plugins/demo/api/count
        ('/api/count', handler.request_count, ['GET']),
        # http://localhost:9090/plugins/demo/api/reset
        ('/api/reset', handler.reset_count, ['PUT'])
    ],
    background=[
    ],
    event=[
        ('flow', handler.on_request)
    ]
)
