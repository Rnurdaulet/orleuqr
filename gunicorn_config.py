import multiprocessing

bind = "127.0.0.1:8000"  # или 0.0.0.0:8001 если доступ через nginx
workers = multiprocessing.cpu_count() * 2 + 1  # 4 * 2 + 1 = 9
threads = 2  # каждый воркер может обслуживать до 2 потоков
worker_class = "gthread"  # или "sync" если у тебя нет I/O операций
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
preload_app = True
