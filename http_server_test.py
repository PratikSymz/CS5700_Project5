from http_server.cache_manager import Cache_Manager

cache = Cache_Manager()
result = cache.load_popularity_data()
print(result)
print(cache.popularity_rate_mapping)
