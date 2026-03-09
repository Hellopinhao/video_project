bind = "127.0.0.1:5000"
workers = 5
worker_class = "gevent"
worker_connections = 1000

timeout = 60
graceful_timeout = 30
keepalive = 5

max_requests = 1000
max_requests_jitter = 100

pidfile = "/run/videoproject-gunicorn.pid"
raw_env = []
