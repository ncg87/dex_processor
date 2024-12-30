bind = "0.0.0.0:8000"  # Expose on all interfaces at port 8000
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'