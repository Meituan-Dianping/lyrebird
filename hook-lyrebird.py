from PyInstaller.utils.hooks import collect_data_files


hiddenimports = [
    'eventlet.hubs.epolls',
    'eventlet.hubs.kqueue',
    'eventlet.hubs.selects',
    'dns',
    'dns.dnssec',
    'dns.e164',
    'dns.hash',
    'dns.namedict',
    'dns.tsigkeyring',
    'dns.update',
    'dns.version',
    'dns.zone',
    'engineio.async_drivers.threading',
    'engineio.async_drivers.eventlet',
    'engineio.async_threading',
    'engineio.async_eventlet',
    'bs4'
]

datas = [
    ('lyrebird/client/static', 'lyrebird/client/static'),
    ('lyrebird/proxy/*', 'lyrebird/proxy')
]
