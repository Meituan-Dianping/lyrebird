from collections import deque


_cache = None


def get_cache():
    global _cache
    if not _cache:
        # todo 此处应根据配置，决定生成ListCache还是RedisCache
        _cache = ListCache()
    return _cache


class ListCache:
    """
    双向序列
    默认最大值1000
    存储流经mock服务的数据
    
    """
    def __init__(self, maxlen=1000):
        self._cache = deque(maxlen=maxlen)

    def add(self, obj):
        self._cache.append(obj)

    def items(self):
        return list(self._cache)

    def get(self, id_):
        for item in list(self._cache):
            if item['id'] != id_:
                continue
            return item

    def clear(self):
        self._cache.clear()
    
    def delete(self, obj):
        self._cache.remove(obj)
    
    def delete_by_ids(self, *ids):
        del_items = []
        for item in list(self._cache):
            if item['id'] in ids:
                del_items.append(item)
        for item in del_items:
            self.delete(item)

class RedisCache:
    """
    如果部署在服务器上，并使用多进程，需要使用redis存储数据，实现多进程共享数据
    
    """
    pass


class FileCache:
    pass
