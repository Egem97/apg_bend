# Configuración de Gunicorn para servidor asíncrono
import multiprocessing
import os

# Configuración básica
bind = "0.0.0.0:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000

# Configuración de rendimiento
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de gevent
gevent_monkey_patch = True

# Configuración de workers
def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
