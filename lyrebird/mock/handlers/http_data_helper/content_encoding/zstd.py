import zstandard as zstd


class ZstdHandler:

    @staticmethod
    def origin2flow(request_data):
        dctx = zstd.ZstdDecompressor()
        _data = dctx.decompress(request_data)
        return _data

    @staticmethod
    def flow2origin(flow_data):
        cctx = zstd.ZstdCompressor()
        _data = cctx.compress(flow_data)
        return _data

    @staticmethod
    def origin2string(request_data):
        dctx = zstd.ZstdDecompressor()
        _data = dctx.decompress(request_data)
        return _data 