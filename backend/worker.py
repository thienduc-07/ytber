"""
Standalone Background Render Worker Daemon.

Runs an independent, distributed render worker instance claiming jobs from
the database-backed queue with atomic leases and heartbeat supervision.

Usage:
    python -m backend.worker
"""

import sys
import os
import signal
import asyncio
import logging

from backend.core.database import init_db_sync
from backend.providers.render_worker import RenderWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("worker_daemon")


async def main():
    logger.info("Initializing Render Worker Daemon...")
    init_db_sync()

    worker = RenderWorker()
    logger.info(f"Worker initialized with ID: {worker.worker_id}")

    stop_event = asyncio.Event()

    def _handle_signal():
        logger.info("Shutdown signal received. Stopping worker loop gracefully...")
        worker._is_running = False
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            pass

    # Start and run the worker loop
    worker_task = asyncio.create_task(worker._worker_queue_loop())

    try:
        await stop_event.wait()
    finally:
        worker._is_running = False
        if not worker_task.done():
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Render Worker Daemon shut down cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker process stopped by user.")
