from __future__ import annotations

import asyncio
import signal


async def noop(ctx: object | None = None) -> None:
    pass


async def process_video(ctx: object | None, job_id: str) -> None:
    pass


class WorkerSettings:
    functions = [noop, process_video]


async def main() -> None:
    # Keep the Docker service alive until the real ARQ worker is wired in a later phase.
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
