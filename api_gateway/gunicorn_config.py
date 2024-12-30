bind = "0.0.0.0:8000"  # Expose on all interfaces at port 8000
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
