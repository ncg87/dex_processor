bind = "0.0.0.0:8000"  # Expose on all interfaces at port 8000
workers = 4            # Adjust based on the number of CPU cores
worker_class = "uvicorn.workers.UvicornWorker"
