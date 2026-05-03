from __future__ import annotations

import asyncio


async def noop(ctx: object | None = None) -> None:
    pass


async def process_video(ctx: object | None, job_id: str) -> None:
    pass


class WorkerSettings:
    functions = [noop, process_video]


async def main() -> None:
    # Keep the Docker service alive until the real ARQ worker is wired in a later phase.
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
