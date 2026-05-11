"""Scheduled task management."""

import asyncio
import signal
from datetime import datetime
from typing import Callable, Optional

from croniter import croniter


class TaskScheduler:
    """Schedule and run periodic tasks."""

    def __init__(self):
        self.tasks: dict[str, dict] = {}
        self.running = False

    def add_task(
        self,
        name: str,
        cron_expr: str,
        callback: Callable,
        *args,
        **kwargs,
    ) -> None:
        """Add a scheduled task.

        Args:
            name: Task name.
            cron_expr: Cron expression (e.g., "0 9 * * *" for daily at 9am).
            callback: Function to call.
            *args: Positional arguments for callback.
            **kwargs: Keyword arguments for callback.
        """
        self.tasks[name] = {
            "cron": croniter(cron_expr, datetime.now()),
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "next_run": None,
        }
        self._update_next_run(name)

    def _update_next_run(self, name: str) -> None:
        """Update next run time for a task."""
        task = self.tasks[name]
        task["next_run"] = task["cron"].get_next(datetime)

    async def run(self) -> None:
        """Start the scheduler loop."""
        self.running = True

        # Handle shutdown signals
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.stop)

        while self.running:
            now = datetime.now()
            sleep_time = 60.0  # Check every minute

            for name, task in self.tasks.items():
                if task["next_run"] and task["next_run"] <= now:
                    # Run the task
                    try:
                        if asyncio.iscoroutinefunction(task["callback"]):
                            await task["callback"](*task["args"], **task["kwargs"])
                        else:
                            task["callback"](*task["args"], **task["kwargs"])
                    except Exception as e:
                        print(f"Task {name} failed: {e}")

                    # Schedule next run
                    self._update_next_run(name)

            await asyncio.sleep(sleep_time)

    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False


# Global scheduler instance
scheduler = TaskScheduler()