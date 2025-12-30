import asyncio

from app.core.logger import init_logger
from worker.task_worker import TaskWorker


def main() -> None:
    init_logger()
    worker = TaskWorker()
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()
