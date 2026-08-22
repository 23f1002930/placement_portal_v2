import json
from flask import current_app

def _client():
    try:
        from redis import Redis
        client=Redis.from_url(current_app.config["REDIS_URL"],socket_connect_timeout=.15,socket_timeout=.15)
        client.ping(); return client
    except Exception: return None

def get_json(key):
    client=_client()
    if not client: return None
    try:
        value=client.get(key); return json.loads(value) if value else None
    except Exception: return None

def set_json(key,value):
    client=_client()
    if client:
        try: client.setex(key,current_app.config["CACHE_TTL"],json.dumps(value))
        except Exception: pass

def invalidate(prefix="dashboard:"):
    client=_client()
    if client:
        try:
            for key in client.scan_iter(prefix+"*"): client.delete(key)
        except Exception: pass
