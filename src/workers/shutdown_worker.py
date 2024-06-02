import os
import signal
import logging


def shutdown_worker():
    """Send a signal to stop the current worker."""
    worker_pid = os.getpid()
    logging.info(
        f"Shutting down worker because shutdown_worker function was called. PID: {worker_pid}")
    os.kill(worker_pid, signal.SIGTERM)