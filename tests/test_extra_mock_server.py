from aiohttp import web
from lyrebird.mock.extra_mock_server.server import init_app
from lyrebird import application

config = {
    "version": "1.6.8",
    "proxy.filters": [
    ],
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }}


async def test_proxy_args_in_path(aiohttp_client, loop):
    application.sync_manager = application.SyncManager()
    app = init_app(config)
    client = await aiohttp_client(app)
    resp = await client.get('/http://www.bing.com')
    assert resp.status == 200
    text = await resp.text()
    assert 'bing' in text


async def test_proxy_args_in_headers(aiohttp_client, loop):
    application.sync_manager = application.SyncManager()
    app = init_app(config)
    client = await aiohttp_client(app)
    resp = await client.get('/http://www.bing.com', headers={
        'MKScheme': 'http',
        'MKOriginHost': 'www.bing.com'
    })
    assert resp.status == 200
    text = await resp.text()
    assert 'bing' in text


async def test_proxy_args_in_query_v1(aiohttp_client, loop):
    application.sync_manager = application.SyncManager()
    app = init_app(config)
    client = await aiohttp_client(app)
    resp = await client.get('/?proxy=http%3A//www.bing.com')
    assert resp.status == 200
    text = await resp.text()
    assert 'bing' in text


async def test_proxy_args_in_query_v2(aiohttp_client, loop):
    application.sync_manager = application.SyncManager()
    app = init_app(config)
    client = await aiohttp_client(app)
    resp = await client.get('/?proxyscheme=http&proxyhost=www.bing.com')
    assert resp.status == 200
    text = await resp.text()
    assert 'bing' in text
