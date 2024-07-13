from functools import lru_cache, wraps
from datetime import datetime, timedelta
from threading import RLock

def cache(seconds: int, max_size: int = 128, typed: bool = False):
def wrapper(f):
lock = RLock()

@wraps(f)
def cached_func(*args, **kwargs):
with lock:
result = cached_func.cache.get(args, None)
if result is None or datetime.utcnow() > result[1]:
result = f(*args, **kwargs), datetime.utcnow() + timedelta(seconds=seconds)
cached_func.cache[args] = result
return result[0]

cached_func.cache = {}

return cached_func

return wrapper