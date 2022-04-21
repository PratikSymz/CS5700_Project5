from collections import OrderedDict
import zlib


class LRUCache:
    # ? Our cache can be of any size, as long as we control that we manage the size of files we put into it
    def __init__(self):
        self.cache = OrderedDict()
        # self.capacity = capacity

    # Return value of the key if found, or return -1 if not
    # Move key to the end if it was accessed, to show that it was most recently used
    def get(self, key: str) -> bytes:
        # if key not in self.cache:
        #     return -1
        # else:
        self.cache.move_to_end(key)
        compressed = self.cache[key]
        try:
            content = zlib.decompress(compressed)
        except:
            print('Decompression error...')
        
        return content      #type:ignore


    # Add the key to dict{}, conventionally.
    # Move key to the end to show that it was most RU
    # Check whether length of dict{} is within our capacity limit
    # If we exceed our capacity, evict the first key (LRU)
    def put(self, key: str, value: bytes) -> None:
        self.cache[key] = zlib.compress(value)
        self.cache.move_to_end(key)
        
        # # ? Probably not needed
        # if len(self.cache) > self.capacity:
        #     self.cache.popitem(last=False)

    def evict(self) -> None:
        self.cache.popitem(last=False)