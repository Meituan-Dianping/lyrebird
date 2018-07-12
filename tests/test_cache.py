from lyrebird.mock.cache import ListCache

def test_list_cache():
    cache = ListCache()
    cache.add('1')
    assert cache.items() == ['1']
    cache.clear()
    assert cache.items() == []

def test_list_cache_max():
    cache = ListCache(maxlen=10)
    for i in range(20):
        cache.add(i)
    assert cache.items()[9] == 19
