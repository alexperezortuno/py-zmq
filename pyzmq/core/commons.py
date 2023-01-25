import os

log_str: str = os.getenv("LOG_FORMAT", f"%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
log_lvl: str = os.getenv("LOG_LEVEL", "debug")
request_headers = {'user-agent': 'pylastic-app/0.2.0', 'content-type': 'application/json'}
